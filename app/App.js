import React, { useState, useEffect, useRef, startTransition } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Button, ImageBackground } from 'react-native';
import { Camera } from 'expo-camera';
import ViewShot from "react-native-view-shot";
import axios from 'axios';

const API_URL = "http://10.166.160.168:5001";

export default function App() {
  const [hasPermission, setHasPermission] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [selectionStart, setSelectionStart] = useState(null);
  const [selectionEnd, setSelectionEnd] = useState(null);

  const imageRef = useRef();
  const cameraRef = useRef(null);

  useEffect(() => {
    console.log("Started");

    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');

    })();
  }, []);


  const takePicture = async () => {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync();
      setCapturedImage(photo.uri);
    }
  };

  const goBack = async () => {
    setCapturedImage(null)
    setSelectionEnd(null)
    setSelectionStart(null)
  }

  const onStartSelect = (e) => {
    const { locationX, locationY } = e.nativeEvent;
    setSelectionStart({ x: locationX, y: locationY });
    //console.log(locationX, locationY)
    setSelectionEnd(null); // Reset end position when we start a new selection
}

  const onMoveSelect = (e) => {
      if (selectionStart) {
          const { locationX, locationY } = e.nativeEvent;
          setSelectionEnd({ x: locationX, y: locationY });
      }
  }

  const cropAndConvertToBase64 = async () => {
    if (!selectionStart || !selectionEnd) return;
  
    await imageRef.current.onLoad;

    /*
    const cords = {
      x1: Math.round(Math.min(selectionStart.x, selectionEnd.x)),
      y1: Math.round(Math.min(selectionStart.y, selectionEnd.y)),
      x2: Math.round(Math.min(selectionStart.x, selectionEnd.x) + Math.abs(selectionEnd.x - selectionStart.x)),
      y2: Math.round(Math.min(selectionStart.y, selectionEnd.y) + Math.abs(selectionEnd.y - selectionStart.y)),
    };
    */

    const cords = {
      left: Math.round(Math.min(selectionStart.x, selectionEnd.x)),
      top: Math.round(Math.min(selectionStart.y, selectionEnd.y)),
      width: Math.round(Math.abs(selectionEnd.x - selectionStart.x)),
      height: Math.round(Math.abs(selectionEnd.y - selectionStart.y)),
    }
    
    /*
    const cords = {
      x1: Math.round(Math.min(selectionStart.x, selectionEnd.x)),
      y1: Math.round(Math.min(selectionStart.y, selectionEnd.y)),
      x2: Math.round(Math.max(selectionStart.x, selectionEnd.x)),
      y2: Math.round(Math.max(selectionStart.y, selectionEnd.y)),
    }
    */

    const uri = await imageRef.current.capture()
    console.log(uri.length)
    await axios.post("http://10.166.160.168:5001/add", {body: uri}, {headers: {...cords}}).catch(err => null)

    //const croppedImage = await captureRef(imageRef, {format: "jpg",result: "data-uri", timeout: 1000,...cropArea})
  
    // croppedImage is now a base64 encoded string
    //await goBack()
  }
  

  if (hasPermission === null) {
    return <View />;
  }
  if (hasPermission === false) {
    return <Text>No access to camera</Text>;
  }


  return (
    <View style={{ flex: 1 }}>
      {capturedImage ? (
        <ViewShot 
        style={{ flex: 1, backgroundImage: capturedImage  }}
        ref={imageRef}
        options={{ result: "base64", format: "jpg", quality: 1  }}
        >
          <ImageBackground 
            source={{ uri: capturedImage }} 
            style={{ flex: 1 }} 
            onStartShouldSetResponder={() => true}
            onMoveShouldSetResponder={() => true}
            onResponderGrant={onStartSelect}
            onResponderMove={onMoveSelect}
            id="test"
          >
            <View style={{ flex: 1, justifyContent: 'space-between', alignItems: 'center' }}>
              {/* Render the selection area */}
              {selectionStart && selectionEnd && (
                <ViewShot
                  style={{
                    position: 'absolute',
                    left: Math.min(selectionStart.x, selectionEnd.x),
                    top: Math.min(selectionStart.y, selectionEnd.y),
                    width: Math.abs(selectionEnd.x - selectionStart.x),
                    height: Math.abs(selectionEnd.y - selectionStart.y),
                    borderColor: 'blue',
                    borderWidth: 2,
                  }}
                />
              )}

              <View style={{ flexDirection: 'row', justifyContent: 'space-between', width: '80%', bottom: 8, position: "absolute" }}>
                <Button title='Go back' onPress={goBack} color="#DBA300" />
                <Button title='Select Text' onPress={cropAndConvertToBase64} disabled={(selectionEnd ? false : true)} color="#DBA300" />
              </View>
            </View>
          </ImageBackground>
        </ViewShot>
      ) : (
        <Camera style={{ flex: 1 }} type={Camera.Constants.Type.back} ref={cameraRef}>
          <View style={{ flex: 1, justifyContent: 'flex-end', alignItems: 'center' }}>
            <Button title='Take picture' onPress={takePicture} />
          </View>
        </Camera>
      )}
    </View>
  );
  }
