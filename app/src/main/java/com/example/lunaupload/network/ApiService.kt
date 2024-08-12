package com.example.lunaupload.network

import retrofit2.Call
import retrofit2.http.GET
import com.example.lunaupload.ui.history.Item

interface ApiService {
    @GET("get_all")
    fun getAllItems(): Call<List<Item>>
}

