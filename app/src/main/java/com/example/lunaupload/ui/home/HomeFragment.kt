package com.example.lunaupload.ui.home

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import com.example.lunaupload.UploadActivity
import com.example.lunaupload.databinding.FragmentHomeBinding

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted: Boolean ->
            try {
                if (isGranted) {
                    Log.d("TakePicture", "Permission granted.")
                    captureImageLauncher.launch(null)
                } else {
                    Log.d("TakePicture", "Permission denied.")
                    Toast.makeText(context, "Permission to access camera is required to take a picture.", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Log.e("HomeFragment", "Error requesting permission", e)
                Toast.makeText(context, "Error requesting permission", Toast.LENGTH_SHORT).show()
            }
        }

    private val captureImageLauncher = registerForActivityResult(ActivityResultContracts.TakePicturePreview()) { bitmap: Bitmap? ->
        try {
            if (bitmap != null) {
                Log.i("HomeFragment", "Image captured successfully.")
                val intent = Intent(activity, UploadActivity::class.java).apply {
                    putExtra("imageBitmap", bitmap)
                }
                startActivity(intent)
            } else {
                Log.w("HomeFragment", "No image captured.")
                Toast.makeText(context, "No image captured", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Log.e("HomeFragment", "Error capturing image", e)
            Toast.makeText(context, "Error capturing image", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return try {
            _binding = FragmentHomeBinding.inflate(inflater, container, false)
            binding.root
        } catch (e: Exception) {
            Log.e("HomeFragment", "Error inflating view", e)
            Toast.makeText(context, "Error inflating view", Toast.LENGTH_SHORT).show()
            null
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.openCameraButton.setOnClickListener {
            checkPermissionAndDispatchIntent()
        }
    }

    private fun checkPermissionAndDispatchIntent() {
        try {
            when {
                ContextCompat.checkSelfPermission(
                    requireContext(),
                    Manifest.permission.CAMERA
                ) == PackageManager.PERMISSION_GRANTED -> {
                    Log.d("TakePicture", "Permission already granted.")
                    captureImageLauncher.launch(null)
                }

                shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {
                    Log.d("TakePicture", "Showing permission rationale.")
                    Toast.makeText(context, "Permission to access camera is required to take a picture.", Toast.LENGTH_SHORT).show()
                    requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                }

                else -> {
                    Log.d("TakePicture", "Requesting permission.")
                    requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                }
            }
        } catch (e: Exception) {
            Log.e("HomeFragment", "Error checking permission and dispatching intent", e)
            Toast.makeText(context, "Error checking permission", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
