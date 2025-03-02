#define pin A0
#define BUFFER_SIZE 3

int val = 0;

int sensor_buffer[BUFFER_SIZE];// = {0,0,0,0,0,0,0,0,0,0};
int buffer_cursor = 0;

void setup() {
  
  Serial.begin(9600);
  pinMode(pin, INPUT);

  for(int i = 0; i < BUFFER_SIZE; i++){
    sensor_buffer[i] = 0;
  }

}

void loop() {
  // put your main code here, to run repeatedly:

  int newVal = 0;

  val = analogRead(A0);
  val = EMGFilter(val);

  //newVal = map(val, 0, 400, 0, 1);

  val = update_buffer(val);
  Serial.println(val);
  delay(10);

}

float EMGFilter(float input)
{
  float output = input;
  {
    static float z1, z2; // filter section state
    float x = output - 0.05159732*z1 - 0.36347401*z2;
    output = 0.01856301*x + 0.03712602*z1 + 0.01856301*z2;
    z2 = z1;
    z1 = x;
  }
  {
    static float z1, z2; // filter section state
    float x = output - -0.53945795*z1 - 0.39764934*z2;
    output = 1.00000000*x + -2.00000000*z1 + 1.00000000*z2;
    z2 = z1;
    z1 = x;
  }
  {
    static float z1, z2; // filter section state
    float x = output - 0.47319594*z1 - 0.70744137*z2;
    output = 1.00000000*x + 2.00000000*z1 + 1.00000000*z2;
    z2 = z1;
    z1 = x;
  }
  {
    static float z1, z2; // filter section state
    float x = output - -1.00211112*z1 - 0.74520226*z2;
    output = 1.00000000*x + -2.00000000*z1 + 1.00000000*z2;
    z2 = z1;
    z1 = x;
  }
  return output;
}

int update_buffer(int sensor_input){
  sensor_buffer[buffer_cursor] = sensor_input;
  int buf_max = -1;
  for(int i = 0; i < BUFFER_SIZE; i++){
    buf_max = sensor_buffer[i] > buf_max ? sensor_buffer[i] : buf_max;
  }
  buffer_cursor = (buffer_cursor + 1) % BUFFER_SIZE;
  return(buf_max);
}
