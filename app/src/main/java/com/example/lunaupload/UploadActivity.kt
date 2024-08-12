package com.example.lunaupload

import android.content.Intent
import android.graphics.Bitmap
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.lunaupload.databinding.ActivityUploadBinding
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import java.io.ByteArrayOutputStream
import java.io.IOException

interface UploadService {
    @Multipart
    @POST("upload")
    suspend fun uploadImage(
        @Part image: MultipartBody.Part
    ): retrofit2.Response<Any>

    @GET("get_results")
    suspend fun getResults(): retrofit2.Response<Any>
}

class UploadActivity : AppCompatActivity() {

    private lateinit var binding: ActivityUploadBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUploadBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val imageBitmap = intent.getParcelableExtra<Bitmap>("imageBitmap")
        if (imageBitmap != null) {
            binding.imageView.setImageBitmap(imageBitmap)
            uploadImage(imageBitmap)
        } else {
            Log.w("UploadActivity", "No image received.")
            Toast.makeText(this, "No image received", Toast.LENGTH_SHORT).show()
        }

        binding.goBackButton.setOnClickListener {
            returnToMainActivity()
        }
    }

    private fun uploadImage(bitmap: Bitmap) {
        val byteArrayOutputStream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, byteArrayOutputStream)
        val byteArray = byteArrayOutputStream.toByteArray()
        val requestFile = byteArray.toRequestBody("image/jpeg".toMediaTypeOrNull())
        val body = MultipartBody.Part.createFormData("file", "image.jpg", requestFile)

        val loggingInterceptor = HttpLoggingInterceptor().apply {
            setLevel(HttpLoggingInterceptor.Level.BODY)
        }
        val client = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl("http://13.200.194.74:8888/")
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val service = retrofit.create(UploadService::class.java)

        lifecycleScope.launch {
            try {
                val response = service.uploadImage(body)
                if (response.isSuccessful) {
                    Log.i("UploadActivity", "Image uploaded successfully.")
                    Toast.makeText(this@UploadActivity, "Image uploaded successfully", Toast.LENGTH_SHORT).show()
                    getResultsAndDisplay()
                } else {
                    val errorBody = response.errorBody()?.string()
                    Log.e("UploadActivity", "Upload failed: $errorBody")
                    Toast.makeText(this@UploadActivity, "Upload failed: $errorBody", Toast.LENGTH_SHORT).show()
                }
            } catch (e: IOException) {
                Log.e("UploadActivity", "Network error while uploading image", e)
                Toast.makeText(this@UploadActivity, "Network error while uploading image", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                Log.e("UploadActivity", "Error uploading image", e)
                Toast.makeText(this@UploadActivity, "Error uploading image", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun getResultsAndDisplay() {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            setLevel(HttpLoggingInterceptor.Level.BODY)
        }
        val client = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl("http://13.200.194.74:8888/")
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val service = retrofit.create(UploadService::class.java)

        lifecycleScope.launch {
            try {
                val response = service.getResults()
                if (response.isSuccessful) {
                    val results = response.body().toString()
                    Log.i("UploadActivity", "Results retrieved successfully.")
                    binding.jsonOutput.text = results
                } else {
                    val errorBody = response.errorBody()?.string()
                    Log.e("UploadActivity", "Failed to get results: $errorBody")
                    Toast.makeText(this@UploadActivity, "Failed to get results: $errorBody", Toast.LENGTH_SHORT).show()
                }
            } catch (e: IOException) {
                Log.e("UploadActivity", "Network error while getting results", e)
                Toast.makeText(this@UploadActivity, "Network error while getting results", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                Log.e("UploadActivity", "Error getting results", e)
                Toast.makeText(this@UploadActivity, "Error getting results", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun returnToMainActivity() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }
}