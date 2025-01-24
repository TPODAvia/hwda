package com.example.myfire;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.util.Log;
import androidx.core.app.NotificationCompat;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

public class FireMsgService extends FirebaseMessagingService {
    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        super.onMessageReceived(remoteMessage);
        Log.d("Msg", "Message received ["+remoteMessage+"]");

        // Create an Intent to launch MainActivity
        Intent intent = new Intent(this, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);

        // This is crucial to indicate that an image is available
        intent.putExtra("Image", "Intruder detected");

        PendingIntent pendingIntent = PendingIntent.getActivity(
                this,
                1410,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_MUTABLE  // If targeting newer APIs
        );

        // Extract info from RemoteMessage
        String info = null;
        if (remoteMessage.getData().size() > 0) {
            info = remoteMessage.getData().get("message");
        }
        if (remoteMessage.getNotification() != null) {
            info = remoteMessage.getNotification().getBody();
        }

        NotificationManager notificationManager =
                (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);

        // For Android O (8.0) and above, you need a notification channel
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    "mychannel",
                    "mychannel",
                    NotificationManager.IMPORTANCE_HIGH
            );
            notificationManager.createNotificationChannel(channel);

            Notification notification = new Notification.Builder(this, "mychannel")
                    .setContentTitle("Message")
                    .setContentText(info)
                    .setSmallIcon(R.drawable.ic_launcher_background)
                    .setContentIntent(pendingIntent)
                    .setAutoCancel(true)
                    .build();

            notificationManager.notify(1410, notification);
        } else {
            // For older Android versions
            NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(this)
                    .setSmallIcon(R.drawable.ic_launcher_background)
                    .setContentTitle("Message")
                    .setContentText(info)
                    .setAutoCancel(true)
                    .setContentIntent(pendingIntent);

            notificationManager.notify(1410, notificationBuilder.build());
        }
    }
}