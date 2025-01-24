package com.example.myfire;

import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Button;
import android.webkit.WebView;
import android.app.ProgressDialog;
import android.view.View;
import android.net.Uri;
import android.util.DisplayMetrics;
import android.util.Log;
import android.content.Intent;
import android.widget.Toast;

import androidx.annotation.NonNull;

import com.bumptech.glide.Glide;
import com.google.firebase.messaging.FirebaseMessaging;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageReference;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.OnFailureListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.android.gms.tasks.Task;

import android.os.Bundle;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {
    ImageView imageView;
    TextView textView;
    TextView textView2;  // etc. if needed
    WebView webView;
    Uri imguri;
    ProgressDialog progressDialog;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        // Bind UI
        Button but1 = findViewById(R.id.button);
        imageView = findViewById(R.id.imageView);
        textView = findViewById(R.id.textView);
        textView2 = findViewById(R.id.textView2);
        TextView textView3 = findViewById(R.id.textView3);
        webView = findViewById(R.id.webView);

        textView.setText("");
        textView2.setText("");
        textView3.setText("");

        // If launched via notification: check intent extras
        if (getIntent().hasExtra("Image")) {
            // Means we have an intruder alert
            // Initialize Firebase Storage
            FirebaseStorage storage = FirebaseStorage.getInstance();
            StorageReference storageRef = storage.getReference();

            // Show a progress dialog while downloading
            progressDialog = new ProgressDialog(this);
            progressDialog.setTitle("Downloading image...");
            progressDialog.show();

            storageRef.child("image.png").getDownloadUrl()
                    .addOnSuccessListener(new OnSuccessListener<Uri>() {
                        @Override
                        public void onSuccess(Uri uri) {
                            imguri = uri;
                            progressDialog.dismiss();
                            textView.setText("Click here to open the image in browser");
                            textView2.setText("Intruder photo:");
                            textView3.setText("Intruder bigger photo in WebView:");

                            // Load image via Glide
                            DisplayMetrics metrics = new DisplayMetrics();
                            getWindowManager().getDefaultDisplay().getMetrics(metrics);

                            Glide.with(getApplicationContext())
                                    .load(imguri)
                                    .override(metrics.widthPixels, metrics.heightPixels)
                                    .into(imageView);

                            // Load image into WebView
                            webView.loadUrl(uri.toString());
                        }
                    })
                    .addOnFailureListener(new OnFailureListener() {
                        @Override
                        public void onFailure(@NonNull Exception e) {
                            progressDialog.dismiss();
                            Log.e("MainActivity", "Failed to load image from Firebase", e);
                        }
                    });
        } else {
            // App opened normally (no PIR event triggered)
        }

        // Clicking textView -> open in default browser
        textView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (imguri != null) {
                    Intent intent = new Intent(Intent.ACTION_VIEW, imguri);
                    // In some emulators, must use chooser
                    startActivity(Intent.createChooser(intent, "Browse with"));
                }
            }
        });

        // Subscribe button
        but1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                FirebaseMessaging.getInstance().subscribeToTopic("alarm");
                FirebaseMessaging.getInstance().getToken()
                        .addOnCompleteListener(new OnCompleteListener<String>() {
                            @Override
                            public void onComplete(@NonNull Task<String> task) {
                                if (!task.isSuccessful()) {
                                    Log.w("MainActivity", "Fetching FCM registration token failed", task.getException());
                                    return;
                                }
                                // Get new FCM registration token
                                String token = task.getResult();
                                Toast.makeText(MainActivity.this,
                                        "Subscribed to alarm channel. Token: " + token,
                                        Toast.LENGTH_SHORT).show();
                                Log.d("MainActivity", "Token: " + token);
                            }
                        });
            }
        });
    }
}