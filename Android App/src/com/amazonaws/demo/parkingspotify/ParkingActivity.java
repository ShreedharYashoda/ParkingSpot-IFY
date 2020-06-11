package com.amazonaws.demo.parkingspotify;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

public class ParkingActivity extends Activity {

    String msg_data = PubSubActivity.getData();
    TextView msg;
//////////////////////////////////////////////////////////////////////SOE Zameer
    ///////////////////////////////////////////////////////////////////EOC Zameer
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_parking);
        msg = findViewById(R.id.msg);
        msg.setText(msg_data);
        PubSubActivity object = new PubSubActivity();
        object.setListener(new PubSubActivity.msgInterface() {
            @Override
            public void sendMessage() {
                            msg.setText(msg_data);
            }
        });

    }

///////////////////////////////////////////////////////////////////////////////////////////////////
//    PubSubActivity pubSubActivity = new PubSubActivity.msgInterface() {
//        @Override
//        public void sendMessage() {
//            msg.setText(msg_data);
//        }
//    }
///////////////////////////////////////////////////////////////////////////////////////////////////
    //interface parkinginterface = new PubSubActivity.msgInterface

///////////////////////////////////////////////////////////////////////////////////////////////////
//    PubSubActivity objectInterface = new PubSubActivity() {
//        @Override
//        public void sendMessage() { msg.setText(msg_data);
//        }
//    };
    /////////////////////////////////////////////////////////////////////////////
    //    objectInterface.setListener(PubSubActivity.msgInterface)
//    objectInterface.setListener(this);
//
//    sendMessage(){
//        msg.setText(msg_data);
//    }
    //    private void runThread() {
//        runOnUiThread(new Thread(new Runnable() {
//            public void run() {
//                while(true){
//                msg.setText(msg_data);}
//            }
//        }));
//    }

}