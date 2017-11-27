void refreshScreen() {

  boolean outout;
  for (int c = 0; c < 5; c++) {
    HMISerial.setComponentValue("st1", 0);
    Serial.println(outout);
  }
  String label;

  for (int i = 1; i < NUM_LIGHTS; i++) {
    HMISerial.setComponentValue("vt" + String(i), int(aLights[i][1]));
    HMISerial.setComponentValue("st" + String(i), int(aLights[i][2]));
    HMISerial.setComponentValue("vl" + String(i), int(aLights[i][3]));
    HMISerial.setComponentValue("cx" + String(i), int(aLights[i][4]));
  }
  HMISerial.sendCommand("t_icons.en=1");
  HMISerial.sendCommand("t_select_type.en=1");
  pBit();
}

byte convertColor(byte color) {
  byte ret = 1;
  switch (color) {
    case 1:
      ret = 1;
      break;
    case 2:
      ret = 2;
      break;
    case 3:
      ret = 3;
      break;
    case 19:
      ret = 2;
      break;
    case 7:
      ret = 3;
      break;
    case 11:
      ret = 4;
      break;
    case 16:
      ret = 5;
      break;
    case 18:
      ret = 6;
      break;
  }
  return ret;

}


void execLightCommand(byte pin, byte sts, int value, int color) {
  byte val = map(value, 0, 254, 0, 100);
  aLights[getPinIdx(pin)][2] = sts; //status
  aLights[getPinIdx(pin)][3] = val; //status
  aLights[getPinIdx(pin)][4] = convertColor(color); //status
  refreshScreen();
}

void setLightConfig(byte pin, byte type, byte mode) {
  //mode 0=insert 2=delete 1=update
  byte idx;
  switch (mode) {
    case 0: //insert
      if (getPinIdx(pin) == -1) {//if the pin not exist
        idx = getFreePinIdx(); //search for the first vacant light
        if (idx != -1) {
          aLights[idx][0] = pin; //pin
          aLights[idx][1] = type; //type
          aLights[idx][2] = OFF; //status
          aLights[idx][3] = 0; //value
          aLights[idx][4] = 1; //color
          //[x][0]=pin [x][1]=type [x][2]=status [x][3]=value [x][4]=color
        }
      }
      else {//if exists update
        idx = getPinIdx(pin); //search for the light to update
        aLights[idx][1] = type; //type
        aLights[idx][2] = OFF; //status
        aLights[idx][3] = 0; //value
        aLights[idx][4] = 1; //color
      }
      break;
    case 1: //delete
      idx = getPinIdx(pin); //search for the light to delete
      if (idx != -1) {
        aLights[idx][0] = NOLIGHT; //pin
        aLights[idx][2] = 999; //status = not visible
      }
      break;
    case 2: //update
      idx = getPinIdx(pin); //search for the light to update
      if (idx != -1) {
        aLights[idx][1] = type; //type
        aLights[idx][2] = OFF; //status
        aLights[idx][3] = 0; //value
        aLights[idx][4] = 1; //color
      }
      break;
  }
  pBit();
  refreshScreen();
}

void setLightGroup(long int RxData[1]) {
  aGroups[0][1] = RxData[2]; //mood1
  aGroups[0][2] = RxData[3]; //mood2
  aGroups[0][3] = RxData[4]; //mood3
  aGroups[0][4] = RxData[5]; //mood4
}

void pBit() {
  tone(9, 1500, 30);
  noTone;
}

void getScreenTouch() {

  uint8_t* touch = HMISerial.listen(); //check for message
  switch (touch[0]) {
    case NEX_RET_ON:
      pBit();
      sendCommand(DEV_ON);
      break;
    case NEX_RET_OFF:
      pBit();
      sendCommand(DEV_OFF);
      break;
    case NEX_RET_DIMMER:
      pBit();
      sendCommand(DEV_DIMMER);
      break;
    case NEX_RET_COLOR1:
      pBit();
      sendCommand(DEV_COLOR1);
      break;
    case NEX_RET_COLOR2:
      pBit();
      sendCommand(DEV_COLOR2);
      break;
    case NEX_RET_COLOR3:
      pBit();
      sendCommand(DEV_COLOR3);
      break;
    case NEX_RET_COLOR4:
      pBit();
      sendCommand(DEV_COLOR4);
      break;
    case NEX_RET_COLOR5:
      pBit();
      sendCommand(DEV_COLOR5);
      break;
    case NEX_RET_COLOR6:
      pBit();
      sendCommand(DEV_COLOR6);
      break;
    case NEX_RET_COLORMONO1:
      pBit();
      sendCommand(DEV_COLORMONO1);
      break;
    case NEX_RET_COLORMONO2:
      pBit();
      sendCommand(DEV_COLORMONO2);
      break;
    case NEX_RET_COLORMONO3:
      pBit();
      sendCommand(DEV_COLORMONO3);
      break;
    case NEX_RET_MOOD1:
      pBit();
      sendCommand(DEV_MOOD1);
      break;
    case NEX_RET_MOOD2:
      pBit();
      sendCommand(DEV_MOOD2);
      break;
    case NEX_RET_MOOD3:
      pBit();
      sendCommand(DEV_MOOD3);
      break;
    case NEX_RET_MOOD4:
      pBit();
      sendCommand(DEV_MOOD4);
      break;
  }
}

