import io
import logging
from enum import Enum
from pathlib import Path
from typing import BinaryIO, Union

from PIL import Image, ImageOps

from app.images.exceptions import ImageResizeError

logger = logging.getLogger(__name__)


class ResizeMode(Enum):
    """Enum for different resize modes."""

    FIT = "fit"  # Resize to fit within dimensions, maintaining aspect ratio
    FILL = "fill"  # Resize and crop to fill dimensions exactly
    STRETCH = "stretch"  # Stretch to exact dimensions (may distort)
    THUMBNAIL = "thumbnail"  # Create thumbnail (fit mode optimized)
    COVER = "cover"  # Resize to cover dimensions, maintaining aspect ratio


class ResamplingFilter(Enum):
    """Enum for resampling filters."""

    NEAREST = Image.Resampling.NEAREST  # Fastest, lowest quality
    BOX = Image.Resampling.BOX  # Fast
    BILINEAR = Image.Resampling.BILINEAR  # Good quality
    HAMMING = Image.Resampling.HAMMING  # Good quality
    BICUBIC = Image.Resampling.BICUBIC  # High quality (default)
    LANCZOS = Image.Resampling.LANCZOS  # Highest quality, slower


class ImageResizer:
    """
    Handles resizing of images with various modes and options.

    Supports multiple resize modes, quality filters, and automatic
    EXIF orientation correction.
    """

    # Default settings
    DEFAULT_RESAMPLING = ResamplingFilter.BICUBIC
    MAX_DIMENSION = 8192
    MIN_DIMENSION = 1

    @staticmethod
    def _validate_dimensions(width: int, height: int) -> None:
        """
        Validate target dimensions.

        Args:
            width: Target width
            height: Target height

        Raises:
            ImageResizeError: If dimensions are invalid
        """
        if width < ImageResizer.MIN_DIMENSION or height < ImageResizer.MIN_DIMENSION:
            raise ImageResizeError(
                f"Dimensions must be at least {ImageResizer.MIN_DIMENSION}px"
            )

        if width > ImageResizer.MAX_DIMENSION or height > ImageResizer.MAX_DIMENSION:
            raise ImageResizeError(
                f"Dimensions cannot exceed {ImageResizer.MAX_DIMENSION}px"
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
    def _calculate_fit_dimensions(
        original_width: int,
        original_height: int,
        target_width: int,
        target_height: int,
    ) -> tuple[int, int]:
        """
        Calculate dimensions to fit image within target size, maintaining aspect ratio.

        Args:
            original_width: Original image width
            original_height: Original image height
            target_width: Target width
            target_height: Target height

        Returns:
            Tuple of (width, height) that fits within target
        """
        aspect_ratio = original_width / original_height
        target_ratio = target_width / target_height

        if aspect_ratio > target_ratio:
            # Width is the limiting factor
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        else:
            # Height is the limiting factor
            new_height = target_height
            new_width = int(target_height * aspect_ratio)

        return new_width, new_height

    @staticmethod
    def _calculate_cover_dimensions(
        original_width: int,
        original_height: int,
        target_width: int,
        target_height: int,
    ) -> tuple[int, int]:
        """
        Calculate dimensions to cover target size, maintaining aspect ratio.

        Args:
            original_width: Original image width
            original_height: Original image height
            target_width: Target width
            target_height: Target height

        Returns:
            Tuple of (width, height) that covers target
        """
        aspect_ratio = original_width / original_height
        target_ratio = target_width / target_height

        if aspect_ratio < target_ratio:
            # Width is the limiting factor
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        else:
            # Height is the limiting factor
            new_height = target_height
            new_width = int(target_height * aspect_ratio)

        return new_width, new_height

    @classmethod
    def _resize_fit(
        cls,
        image: Image.Image,
        width: int,
        height: int,
        resampling: ResamplingFilter,
    ) -> Image.Image:
        """Resize image to fit within dimensions, maintaining aspect ratio."""
        new_width, new_height = cls._calculate_fit_dimensions(
            image.width, image.height, width, height
        )
        return image.resize((new_width, new_height), resampling.value)

    @classmethod
    def _resize_fill(
        cls,
        image: Image.Image,
        width: int,
        height: int,
        resampling: ResamplingFilter,
    ) -> Image.Image:
        """Resize and crop image to fill dimensions exactly."""
        # First, resize to cover the target dimensions
        new_width, new_height = cls._calculate_cover_dimensions(
            image.width, image.height, width, height
        )
        resized = image.resize((new_width, new_height), resampling.value)

        # Then crop to exact dimensions (centered)
        left = (new_width - width) // 2
        top = (new_height - height) // 2
        right = left + width
        bottom = top + height

        return resized.crop((left, top, right, bottom))

    @staticmethod
    def _resize_stretch(
        image: Image.Image,
        width: int,
        height: int,
        resampling: ResamplingFilter,
    ) -> Image.Image:
        """Stretch image to exact dimensions (may distort)."""
        return image.resize((width, height), resampling.value)

    @classmethod
    def _resize_thumbnail(
        cls,
        image: Image.Image,
        width: int,
        height: int,
    ) -> Image.Image:
        """Create thumbnail using PIL's optimized thumbnail method."""
        img_copy = image.copy()
        img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)
        return img_copy

    @classmethod
    def _resize_cover(
        cls,
        image: Image.Image,
        width: int,
        height: int,
        resampling: ResamplingFilter,
    ) -> Image.Image:
        """Resize to cover dimensions, maintaining aspect ratio (no crop)."""
        new_width, new_height = cls._calculate_cover_dimensions(
            image.width, image.height, width, height
        )
        return image.resize((new_width, new_height), resampling.value)

    @classmethod
    def resize_bytes(
        cls,
        image_bytes: bytes,
        width: int,
        height: int,
        mode: Union[str, ResizeMode] = ResizeMode.FIT,
        resampling: Union[str, ResamplingFilter] = DEFAULT_RESAMPLING,
        format: str | None = None,
        quality: int = 85,
        optimize: bool = True,
    ) -> bytes:
        """
        Resize image bytes.

        Args:
            image_bytes: Original image as bytes
            width: Target width in pixels
            height: Target height in pixels
            mode: Resize mode (fit, fill, stretch, thumbnail, cover)
            resampling: Resampling filter for quality
            format: Output format (if None, uses original format)
            quality: Quality for lossy formats (1-100)
            optimize: Whether to optimize the output

        Returns:
            Resized image as bytes

        Raises:
            ImageResizeError: If resizing fails
            ValueError: If parameters are invalid
        """
        try:
            # Validate dimensions
            cls._validate_dimensions(width, height)

            # Normalize mode
            if isinstance(mode, str):
                try:
                    mode = ResizeMode(mode.lower())
                except ValueError:
                    raise ValueError(
                        f"Unsupported resize mode: {mode}. "
                        f"Supported modes: {', '.join(m.value for m in ResizeMode)}"
                    )

            # Normalize resampling filter
            if isinstance(resampling, str):
                try:
                    resampling = ResamplingFilter[resampling.upper()]
                except KeyError:
                    raise ValueError(
                        f"Unsupported resampling filter: {resampling}. "
                        f"Supported filters: {', '.join(f.name for f in ResamplingFilter)}"
                    )

            # Load image
            with Image.open(io.BytesIO(image_bytes)) as image:
                original_size = (image.width, image.height)
                original_format = image.format

                # Correct orientation
                image = cls._correct_orientation(image)

                # Perform resize based on mode
                if mode == ResizeMode.FIT:
                    resized = cls._resize_fit(image, width, height, resampling)
                elif mode == ResizeMode.FILL:
                    resized = cls._resize_fill(image, width, height, resampling)
                elif mode == ResizeMode.STRETCH:
                    resized = cls._resize_stretch(image, width, height, resampling)
                elif mode == ResizeMode.THUMBNAIL:
                    resized = cls._resize_thumbnail(image, width, height)
                elif mode == ResizeMode.COVER:
                    resized = cls._resize_cover(image, width, height, resampling)
                else:
                    raise ValueError(f"Unknown resize mode: {mode}")

                # Prepare save options
                output_format = format or original_format or "PNG"
                save_kwargs = {"format": output_format, "optimize": optimize}

                # Add quality for lossy formats
                if output_format.upper() in ("JPEG", "JPG", "WEBP"):
                    save_kwargs["quality"] = quality

                # Convert to bytes
                output_buffer = io.BytesIO()
                resized.save(output_buffer, **save_kwargs)
                output_buffer.seek(0)

                logger.info(
                    f"Successfully resized image from {original_size} to "
                    f"({resized.width}x{resized.height}) using {mode.value} mode "
                    f"(size: {len(image_bytes)} -> {output_buffer.getbuffer().nbytes} bytes)"
                )

                return output_buffer.getvalue()

        except Exception as e:
            if isinstance(e, (ImageResizeError, ValueError)):
                raise
            logger.error(f"Failed to resize image: {e}")
            raise ImageResizeError(f"Image resizing failed: {str(e)}") from e

    @classmethod
    def resize_file(
        cls,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        width: int,
        height: int,
        mode: Union[str, ResizeMode] = ResizeMode.FIT,
        resampling: Union[str, ResamplingFilter] = DEFAULT_RESAMPLING,
        format: str | None = None,
        quality: int = 85,
        optimize: bool = True,
    ) -> None:
        """
        Resize image file.

        Args:
            input_path: Path to input image file
            output_path: Path to output image file
            width: Target width in pixels
            height: Target height in pixels
            mode: Resize mode
            resampling: Resampling filter
            format: Output format (if None, inferred from output_path)
            quality: Quality for lossy formats
            optimize: Whether to optimize the output

        Raises:
            ImageResizeError: If resizing fails
            FileNotFoundError: If input file doesn't exist
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Infer format from output path if not provided
        if format is None:
            extension = output_path.suffix.lstrip(".").upper()
            if extension:
                format = extension

        # Read input file
        with open(input_path, "rb") as f:
            image_bytes = f.read()

        # Resize
        resized_bytes = cls.resize_bytes(
            image_bytes=image_bytes,
            width=width,
            height=height,
            mode=mode,
            resampling=resampling,
            format=format,
            quality=quality,
            optimize=optimize,
        )

        # Write output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(resized_bytes)

        logger.info(f"Resized {input_path} -> {output_path}")

    @classmethod
    def resize_stream(
        cls,
        input_stream: BinaryIO,
        output_stream: BinaryIO,
        width: int,
        height: int,
        mode: Union[str, ResizeMode] = ResizeMode.FIT,
        resampling: Union[str, ResamplingFilter] = DEFAULT_RESAMPLING,
        format: str | None = None,
        quality: int = 85,
        optimize: bool = True,
    ) -> None:
        """
        Resize image from input stream to output stream.

        Args:
            input_stream: Input binary stream
            output_stream: Output binary stream
            width: Target width in pixels
            height: Target height in pixels
            mode: Resize mode
            resampling: Resampling filter
            format: Output format
            quality: Quality for lossy formats
            optimize: Whether to optimize the output

        Raises:
            ImageResizeError: If resizing fails
        """
        image_bytes = input_stream.read()
        resized_bytes = cls.resize_bytes(
            image_bytes=image_bytes,
            width=width,
            height=height,
            mode=mode,
            resampling=resampling,
            format=format,
            quality=quality,
            optimize=optimize,
        )
        output_stream.write(resized_bytes)

    @classmethod
    def resize_to_width(
        cls,
        image_bytes: bytes,
        width: int,
        resampling: Union[str, ResamplingFilter] = DEFAULT_RESAMPLING,
        format: str | None = None,
        quality: int = 85,
    ) -> bytes:
        """
        Resize image to specific width, maintaining aspect ratio.

        Args:
            image_bytes: Original image as bytes
            width: Target width in pixels
            resampling: Resampling filter
            format: Output format
            quality: Quality for lossy formats

        Returns:
            Resized image as bytes
        """
        with Image.open(io.BytesIO(image_bytes)) as image:
            aspect_ratio = image.height / image.width
            height = int(width * aspect_ratio)

        return cls.resize_bytes(
            image_bytes=image_bytes,
            width=width,
            height=height,
            mode=ResizeMode.STRETCH,
            resampling=resampling,
            format=format,
            quality=quality,
        )

    @classmethod
    def resize_to_height(
        cls,
        image_bytes: bytes,
        height: int,
        resampling: Union[str, ResamplingFilter] = DEFAULT_RESAMPLING,
        format: str | None = None,
        quality: int = 85,
    ) -> bytes:
        """
        Resize image to specific height, maintaining aspect ratio.

        Args:
            image_bytes: Original image as bytes
            height: Target height in pixels
            resampling: Resampling filter
            format: Output format
            quality: Quality for lossy formats

        Returns:
            Resized image as bytes
        """
        with Image.open(io.BytesIO(image_bytes)) as image:
            aspect_ratio = image.width / image.height
            width = int(height * aspect_ratio)

        return cls.resize_bytes(
            image_bytes=image_bytes,
            width=width,
            height=height,
            mode=ResizeMode.STRETCH,
            resampling=resampling,
            format=format,
            quality=quality,
        )

    @classmethod
    def create_thumbnail(
        cls,
        image_bytes: bytes,
        max_size: int = 150,
        format: str = "JPEG",
        quality: int = 85,
    ) -> bytes:
        """
        Create a square thumbnail.

        Args:
            image_bytes: Original image as bytes
            max_size: Maximum dimension for thumbnail
            format: Output format
            quality: Quality for lossy formats

        Returns:
            Thumbnail as bytes
        """
        return cls.resize_bytes(
            image_bytes=image_bytes,
            width=max_size,
            height=max_size,
            mode=ResizeMode.FILL,
            format=format,
            quality=quality,
        )

    @classmethod
    def resize_multiple(
        cls,
        image_bytes: bytes,
        sizes: list[tuple[int, int]],
        mode: Union[str, ResizeMode] = ResizeMode.FIT,
        resampling: Union[str, ResamplingFilter] = DEFAULT_RESAMPLING,
        format: str | None = None,
        quality: int = 85,
    ) -> dict[tuple[int, int], bytes]:
        """
        Resize image to multiple sizes at once.

        Args:
            image_bytes: Original image as bytes
            sizes: List of (width, height) tuples
            mode: Resize mode
            resampling: Resampling filter
            format: Output format
            quality: Quality for lossy formats

        Returns:
            Dictionary mapping (width, height) to resized image bytes
        """
        results = {}

        for width, height in sizes:
            try:
                resized = cls.resize_bytes(
                    image_bytes=image_bytes,
                    width=width,
                    height=height,
                    mode=mode,
                    resampling=resampling,
                    format=format,
                    quality=quality,
                )
                results[(width, height)] = resized
            except Exception as e:
                logger.error(f"Failed to resize to {width}x{height}: {e}")
                results[(width, height)] = None

        return results
