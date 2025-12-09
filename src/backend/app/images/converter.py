import io
import logging
from pathlib import Path
from typing import Any, BinaryIO, Union

from PIL import Image, ImageOps

from app.images.exceptions import ImageConversionError
from app.images.formats import ImageFormat

logger = logging.getLogger(__name__)


class ImageConverter:
    """
    Handles conversion of images between different formats.

    Supports JPEG, PNG, and WEBP formats with automatic optimization
    and EXIF orientation correction.
    """

    # Quality settings for lossy formats
    DEFAULT_JPEG_QUALITY = 85
    DEFAULT_WEBP_QUALITY = 85

    # Maximum image dimensions to prevent memory issues
    MAX_IMAGE_DIMENSION = 8192

    # Supported formats mapping
    FORMAT_MAPPING = {
        ImageFormat.JPEG: "JPEG",
        ImageFormat.JPG: "JPEG",
        ImageFormat.PNG: "PNG",
        ImageFormat.WEBP: "WEBP",
    }

    @staticmethod
    def _normalize_format(format_value: Union[str, ImageFormat]) -> ImageFormat:
        """
        Normalize format input to ImageFormat enum.

        Args:
            format_value: Format as string or ImageFormat enum

        Returns:
            ImageFormat enum value

        Raises:
            ValueError: If format is not supported
        """
        if isinstance(format_value, str):
            try:
                return ImageFormat(format_value.lower())
            except ValueError:
                raise ValueError(
                    f"Unsupported format: {format_value}. "
                    f"Supported formats: {', '.join(f.value for f in ImageFormat)}"
                )
        return format_value

    @staticmethod
    def _validate_image(image: Image.Image) -> None:
        """
        Validate image dimensions and properties.

        Args:
            image: PIL Image object

        Raises:
            ImageConversionError: If image is invalid
        """
        if (
            image.width > ImageConverter.MAX_IMAGE_DIMENSION
            or image.height > ImageConverter.MAX_IMAGE_DIMENSION
        ):
            raise ImageConversionError(
                f"Image dimensions ({image.width}x{image.height}) exceed "
                f"maximum allowed ({ImageConverter.MAX_IMAGE_DIMENSION}x{ImageConverter.MAX_IMAGE_DIMENSION})"
            )

        if image.width == 0 or image.height == 0:
            raise ImageConversionError(
                "Image has invalid dimensions (0 width or height)"
            )

    @staticmethod
    def _correct_orientation(image: Image.Image) -> Image.Image:
        """
        Correct image orientation based on EXIF data.

        Args:
            image: PIL Image object

        Returns:
            Image with corrected orientation
        """
        try:
            return ImageOps.exif_transpose(image)
        except Exception as e:
            logger.warning(f"Failed to correct image orientation: {e}")
            return image

    @staticmethod
    def _prepare_image_for_format(
        image: Image.Image, target_format: ImageFormat
    ) -> Image.Image:
        """
        Prepare image for the target format (handle transparency, color modes, etc.).

        Args:
            image: PIL Image object
            target_format: Target format

        Returns:
            Prepared image
        """
        # Handle transparency for formats that don't support it
        if target_format in (ImageFormat.JPEG, ImageFormat.JPG):
            if image.mode in ("RGBA", "LA", "P"):
                # Create white background for transparent images
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                if image.mode in ("RGBA", "LA"):
                    background.paste(
                        image, mask=image.split()[-1]
                    )  # Use alpha channel as mask
                    return background
            elif image.mode != "RGB":
                return image.convert("RGB")

        # Convert palette mode to RGBA for better quality
        elif image.mode == "P":
            return image.convert("RGBA")

        return image

    @classmethod
    def convert_bytes(
        cls,
        image_bytes: bytes,
        target_format: Union[str, ImageFormat],
        quality: int | None = None,
        optimize: bool = True,
    ) -> bytes:
        """
        Convert image bytes to a different format.

        Args:
            image_bytes: Original image as bytes
            target_format: Target format (string or ImageFormat enum)
            quality: Quality for lossy formats (1-100). If None, uses defaults.
            optimize: Whether to optimize the output image

        Returns:
            Converted image as bytes

        Raises:
            ImageConversionError: If conversion fails
            ValueError: If format is not supported
        """
        try:
            # Normalize format
            target_format_enum = cls._normalize_format(target_format)
            pil_format = cls.FORMAT_MAPPING[target_format_enum]

            # Load image
            with Image.open(io.BytesIO(image_bytes)) as image:
                # Validate image
                cls._validate_image(image)

                # Correct orientation
                image = cls._correct_orientation(image)

                # Prepare image for target format
                image = cls._prepare_image_for_format(image, target_format_enum)

                # Prepare save options
                save_kwargs = {"format": pil_format, "optimize": optimize}

                # Add quality parameter for lossy formats
                if target_format_enum in (ImageFormat.JPEG, ImageFormat.JPG):
                    save_kwargs["quality"] = (
                        quality if quality is not None else cls.DEFAULT_JPEG_QUALITY
                    )
                elif target_format_enum == ImageFormat.WEBP:
                    save_kwargs["quality"] = (
                        quality if quality is not None else cls.DEFAULT_WEBP_QUALITY
                    )

                # Convert to bytes
                output_buffer = io.BytesIO()
                image.save(output_buffer, **save_kwargs)
                output_buffer.seek(0)

                logger.info(
                    f"Successfully converted image to {target_format_enum.value} "
                    f"(size: {len(image_bytes)} -> {output_buffer.getbuffer().nbytes} bytes)"
                )

                return output_buffer.getvalue()

        except Exception as e:
            if isinstance(e, (ImageConversionError, ValueError)):
                raise
            logger.error(f"Failed to convert image: {e}")
            raise ImageConversionError(f"Image conversion failed: {str(e)}") from e

    @classmethod
    def convert_file(
        cls,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        target_format: Union[str, ImageFormat] | None = None,
        quality: int | None = None,
        optimize: bool = True,
    ) -> None:
        """
        Convert image file to a different format.

        Args:
            input_path: Path to input image file
            output_path: Path to output image file
            target_format: Target format. If None, inferred from output_path extension
            quality: Quality for lossy formats (1-100). If None, uses defaults.
            optimize: Whether to optimize the output image

        Raises:
            ImageConversionError: If conversion fails
            ValueError: If format is not supported or cannot be inferred
            FileNotFoundError: If input file doesn't exist
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Infer target format from output path if not provided
        if target_format is None:
            extension = output_path.suffix.lstrip(".").lower()
            if not extension:
                raise ValueError(
                    "Cannot infer target format from output path without extension"
                )
            target_format = extension

        # Read input file
        with open(input_path, "rb") as f:
            image_bytes = f.read()

        # Convert
        converted_bytes = cls.convert_bytes(
            image_bytes, target_format, quality=quality, optimize=optimize
        )

        # Write output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(converted_bytes)

        logger.info(f"Converted {input_path} -> {output_path}")

    @classmethod
    def convert_stream(
        cls,
        input_stream: BinaryIO,
        output_stream: BinaryIO,
        target_format: Union[str, ImageFormat],
        quality: int | None = None,
        optimize: bool = True,
    ) -> None:
        """
        Convert image from input stream to output stream.

        Args:
            input_stream: Input binary stream
            output_stream: Output binary stream
            target_format: Target format
            quality: Quality for lossy formats (1-100). If None, uses defaults.
            optimize: Whether to optimize the output image

        Raises:
            ImageConversionError: If conversion fails
            ValueError: If format is not supported
        """
        image_bytes = input_stream.read()
        converted_bytes = cls.convert_bytes(
            image_bytes, target_format, quality=quality, optimize=optimize
        )
        output_stream.write(converted_bytes)

    @staticmethod
    def get_image_info(image_bytes: bytes) -> dict[str, Any]:
        """
        Get information about an image.

        Args:
            image_bytes: Image as bytes

        Returns:
            Dictionary with image information (format, size, mode, etc.)

        Raises:
            ImageConversionError: If image cannot be read
        """
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                return {
                    "format": image.format,
                    "mode": image.mode,
                    "size": image.size,
                    "width": image.width,
                    "height": image.height,
                    "info": image.info,
                }
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            raise ImageConversionError(f"Failed to read image: {str(e)}") from e

    @staticmethod
    def is_valid_image(image_bytes: bytes) -> bool:
        """
        Check if bytes represent a valid image.

        Args:
            image_bytes: Bytes to check

        Returns:
            True if valid image, False otherwise
        """
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                image.verify()
            return True
        except Exception:
            return False
