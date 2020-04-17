#include <Encoder.h>

const int pullup_start_index = 2;
const int pullup_end_index = pullup_start_index+5;
const int normal_end_index = pullup_end_index+6;

const int num_pins = normal_end_index - pullup_start_index;

static int state[num_pins];
static int counter = 0;

Encoder left_enc(6+2, 7+2);
Encoder right_enc(9+2, 8+2);

void send_report()
{
    int index = 0;
    /* The json shall include a magic element for ID */
    /* Send function shall be on its own */
    /* Return a send whenever data is received.. */
    Serial.print("{\"magic\": 1337, ");
    for (int i = 0; i < num_pins-1; i++)
    {
        Serial.print("\"");
        Serial.print(i);
        Serial.print("\": ");
        Serial.print(state[i]);
        Serial.print(", ");
        index += 1;
    }
    Serial.print("\"");
    Serial.print(index);
    Serial.print("\": ");
    Serial.print(state[index]);
    Serial.print(",");
    Serial.print("\"left_enc_count\":");
    Serial.print(left_enc.read());
    Serial.print(",");
    Serial.print("\"right_enc_count\":");
    Serial.print(right_enc.read());
    Serial.print("}");
    Serial.print("\n");
}

// the setup routine runs once when you press reset:
void setup() {
    Serial.begin(115200);
    // make the pushbutton's pin an input:
    for (int i = pullup_start_index; i < pullup_end_index; i++)
    {
        pinMode(i, INPUT_PULLUP);
    }
    for (int i = pullup_end_index; i < normal_end_index; i++)
    {
        pinMode(i, INPUT);
    }
    send_report();
}

bool check()
{
    bool ret = false;
    int index = 0;
    for (int i = pullup_start_index; i < normal_end_index; i++)
    {
        int buttonState = digitalRead(i);
        if (buttonState != state[index])
        {
            ret = true;
        }
        state[index] = buttonState;
        index += 1;
    }
    return ret;
}

// the loop routine runs over and over again forever:
void loop() {
    if (check() || counter > 1000)
    {
        send_report();
        counter = 0;
    }
    delay(1);
    counter += 1;
}
