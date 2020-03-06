
#include <stdio.h>
#include <Bounce.h>
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

// GUItool: begin automatically generated code
AudioInputI2S            i2s2;           //xy=105,63
AudioAnalyzePeak         peak1;          //xy=278,108
AudioRecordQueue         queue1;         //xy=281,63
AudioPlaySdRaw           playRaw1;       //xy=302,157
AudioOutputI2S           i2s1;           //xy=470,120
AudioConnection          patchCord1(i2s2, 0, queue1, 0);
AudioConnection          patchCord2(i2s2, 0, peak1, 0);
AudioConnection          patchCord3(playRaw1, 0, i2s1, 0);
AudioConnection          patchCord4(playRaw1, 0, i2s1, 1);
AudioControlSGTL5000     sgtl5000_1;     //xy=265,212

Bounce buttonRecord = Bounce(0, 8);
Bounce buttonStop =   Bounce(1, 8);  // 8 = 8 ms debounce time
Bounce buttonPlay =   Bounce(2, 8);
Bounce buttonLPF = Bounce(3,8);
Bounce buttonHPF= Bounce(4,8);
Bounce buttonBPF= Bounce(5,8);
double a2history=0, a3history=0;
Bounce buttonPlay2 = Bounce(6,8);
//int PreviousKnobLPF=CurrentKnobLPF;
//int knobHPF=analogRead(A2);


const int myInput = AUDIO_INPUT_MIC;


#define SDCARD_CS_PIN    10
#define SDCARD_MOSI_PIN  7
#define SDCARD_SCK_PIN   14


// Remember which mode we're doing
int mode = 0;  // 0=stopped, 1=recording, 2=playing;
double a2 = analogRead(A2)*20;
double a3 = analogRead(A3)*20;

// The file where data is recorded
File frec;


void setup() {
  // Serial communication from Teensy to Python
  Serial.begin(705600);
  // Configure the pushbutton pins
  pinMode(0, INPUT_PULLUP);
  pinMode(1, INPUT_PULLUP);
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(5,INPUT_PULLUP);
  pinMode(6,INPUT_PULLUP); 

  // Audio connections require memory, and the record queue
  // uses this memory to buffer incoming audio.
  AudioMemory(60);

  // Enable the audio shield, select input, and enable output
  sgtl5000_1.enable();
  sgtl5000_1.inputSelect(myInput);
  sgtl5000_1.volume(0.5);

  // Initialize the SD card
  SPI.setMOSI(SDCARD_MOSI_PIN);
  SPI.setSCK(SDCARD_SCK_PIN);
  if (!(SD.begin(SDCARD_CS_PIN))) {
    // stop here if no SD card, but print a message
    while (1) {
      Serial.println("Unable to access the SD card");
      delay(500);
    }
  }
  a2history = analogRead(A2)*20;
  //Serial.println(a2history);
  a3history = analogRead(A3)*20;
  
}

void loop() {
  // First, read the buttons
  buttonRecord.update();
  buttonStop.update();
  buttonPlay.update();
  buttonLPF.update();
  buttonHPF.update();
  buttonBPF.update();
  buttonPlay2.update();

  if (mode==0){
  Potentiometer1();
  }

  if(buttonLPF.fallingEdge()){
    if (mode==0) LPFtransfer();
  }
  if(buttonHPF.fallingEdge()){
    if (mode==0) HPFtransfer();
  }
  if(buttonBPF.fallingEdge()){
    if (mode==0) BPFtransfer();
  }
  
  // Respond to button presses
  if (buttonRecord.fallingEdge()) {
    //Serial.println("Record Button Press");
    if (mode == 2) stopPlaying();
    if (mode == 0) startRecording();
  }
  if (buttonStop.fallingEdge()) {
    //Serial.println("Stop Button Press");
    if (mode == 1) stopRecording();
    if (mode == 2) stopPlaying();
  }
  if (buttonStop.fallingEdge()){
    if (mode==1) startTransfer();
  }
  if (buttonPlay.fallingEdge()) {
    //Serial.println("Play Button Press");
    if (mode == 1) stopRecording();
    if (mode == 0) startPlaying();
  }

  if(buttonPlay2.fallingEdge()){
     if (mode == 1) stopRecording();
    if (mode == 0) startPlaying2();
  }

  // If we're playing or recording, carry on...
  if (mode == 1) {
    continueRecording();
  }
  if (mode == 2) {
    continuePlaying();
  }

  // when using a microphone, continuously adjust gain
  if (myInput == AUDIO_INPUT_MIC) adjustMicLevel();
}


void startRecording() {
  //Serial.println("startRecording");
  if (SD.exists("RECORD.RAW")) {
    // The SD library writes new data to the end of the
    // file, so to start a new recording, the old file
    // must be deleted before new data is written.
    SD.remove("RECORD.RAW");
  }
  frec = SD.open("RECORD.RAW", FILE_WRITE);
  if (frec) {
    queue1.begin();
    mode = 1;
  }
}

void continueRecording() {
  if (queue1.available() >= 2) {
    byte buffer[512];
    // Fetch 2 blocks from the audio library and copy
    // into a 512 byte buffer.  The Arduino SD library
    // is most efficient when full 512 byte sector size
    // writes are used.
    memcpy(buffer, queue1.readBuffer(), 256);
    //Serial.write(buffer,64);
    queue1.freeBuffer();
    memcpy(buffer+256, queue1.readBuffer(), 256);
    queue1.freeBuffer();
    // write all 512 bytes to the SD card
    elapsedMicros usec = 0;
    frec.write(buffer, 512);
    //Serial.write(buffer, 64);
    //Serial.write(buffer+64, 64);

  }
}

void stopRecording() {
  queue1.end();
  if (mode == 1) {
    while (queue1.available() > 0) {
      frec.write((byte*)queue1.readBuffer(), 256);
      
      queue1.freeBuffer();
    }
    frec.close();
  }
  mode = 1;
}


void startPlaying() {
  //Serial.println("startPlaying");
  playRaw1.play("RECORD.RAW");
  mode = 2;
}
void startPlaying2() {
  //Serial.println("startPlaying");
  playRaw1.play("RECORD2.RAW");
  mode = 2;
}

void continuePlaying() {
  if (!playRaw1.isPlaying()) {
    playRaw1.stop();
    mode = 0;
  }
}

void stopPlaying() {
  //Serial.println("stopPlaying");
  if (mode == 2) playRaw1.stop();
  mode = 0;
}

void startTransfer(){
  //Serial.begin(9600);
  Serial.write('0');
  File dataFile=SD.open("RECORD.RAW");
  while(dataFile.available()){
    Serial.write(dataFile.read());
  }
  dataFile.close();
  
  File dataFile2=SD.open("RECORD.RAW");
  if (SD.exists("RECORD2.RAW")) {
  SD.remove("RECORD2.RAW");
  }
  File frec2 = SD.open("RECORD2.RAW", FILE_WRITE);
  //delay(10000);
  //byte buffer[512];
  //memcpy(buffer, Serial.read(), 256);
  //memcpy(buffer+256, Serial.read(), 256);
  //frec.write(buffer, 512);
  //frec.write((byte*)queue1.readBuffer(), 256);
  //delay(5000);
  while(!Serial.available()){
    
  }
  while(Serial.available()){
  frec2.write(Serial.read());
  }
  //int x=0;
  //if (frec2){
    //while(Serial.available()>0){
      //frec2.write(Serial.read());
      //delay(10);
      //x=dataFile2.read();
    //}
  //}
  //while(!Serial.available()){
    
  //}
  //int g=0;
  //int x=0;
  //delay(10);
  //if (Serial.available()>0){
  //g=(Serial.read());
  //x=x+1;
  //frec2.write(g);
  //}
  //frec2.write(g);
  frec2.close();
  //incomingByte=Serial.read();
  //Serial.write('q');
  mode=0;
  
}
void adjustMicLevel(){
}

void LPFtransfer(){
  Serial.write("1");
}

void HPFtransfer(){
  Serial.write("2");
}
void BPFtransfer(){
  Serial.write("3");
}

void Potentiometer1(){
  double a2 = analogRead(A2)*20;
  double a3 = analogRead(A3)*20;
    if (a2 > a2history + 50*20 || a2 < a2history - 50*20) {
      Serial.write("4");
      Serial.println(a2);
      a2history = a2;
      
    }
        if (a3 > a3history + 50*20 || a3 < a3history - 50*20) {
      Serial.write("5");
      Serial.println(a3);
      a3history = a3;
    }
}
