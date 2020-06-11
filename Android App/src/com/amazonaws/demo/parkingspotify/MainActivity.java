package com.amazonaws.demo.parkingspotify;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Toast;

public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public void parkingButton(View view) {
        Intent intent = new Intent(this, ParkingActivity.class);
        startActivity(intent);

    }
    public void test(View view){
         //Displaying simple Toast message
        Toast.makeText(getApplicationContext(),
                "Only for developers!",
                Toast.LENGTH_LONG)
                .show();
//        Intent intent = new Intent(this,PubSubActivity.class );
//        startActivity(intent);
    }
    public void mqttTest(View view){

        Intent intent = new Intent(this,MqttTestActivity.class);
        startActivity(intent);
    }
}
