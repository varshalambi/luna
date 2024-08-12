package com.example.lunaupload

import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.NavController
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {

    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        try {
            val navHostFragment = supportFragmentManager
                .findFragmentById(R.id.nav_host_fragment1) as NavHostFragment?
            if (navHostFragment != null) {
                navController = navHostFragment.navController

                val bottomNavView = findViewById<BottomNavigationView>(R.id.nav_view)
                if (bottomNavView != null) {
                    bottomNavView.setupWithNavController(navController)
                } else {
                    Log.e("MainActivity", "BottomNavigationView not found")
                    showToast("Navigation view error")
                }
            } else {
                Log.e("MainActivity", "NavHostFragment not found")
                showToast("Navigation host error")
            }
        } catch (e: Exception) {
            Log.e("MainActivity", "Error initializing navigation", e)
            showToast("Unexpected error occurred")
        }
    }

    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }
}
