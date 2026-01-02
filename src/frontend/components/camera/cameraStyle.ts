import { StyleSheet } from 'react-native';

export const cameraStyles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: 'black',
    },
    permissionContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    camera: {
        flex: 1,
        width: '100%',
    },
    closeButtonContainer: {
        position: 'absolute',
        top: 0,
        right: 0,
        zIndex: 10,
        paddingHorizontal: 16,
        paddingTop: 40,
    },

    mainButtonContainer: {
        position: 'absolute',
        bottom: 40,
        flexDirection: 'row',
        width: '100%',
        justifyContent: 'space-around',
        alignItems: 'center',
        paddingHorizontal: 16,
    },
    previewButtonContainer: {
        position: 'absolute',
        bottom: 40,
        flexDirection: 'row',
        width: '100%',
        justifyContent: 'space-between',
        paddingHorizontal: 40,
        alignItems: 'center',
    },
    captureButton: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: 'rgba(255,255,255,0.7)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    captureCircle: {
        width: 70,
        height: 70,
        borderRadius: 35,
        backgroundColor: 'white',
        borderWidth: 2,
        borderColor: 'black',
    }
});
