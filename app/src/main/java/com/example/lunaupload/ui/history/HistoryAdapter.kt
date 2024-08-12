import android.util.Log
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.bumptech.glide.load.engine.GlideException
import com.bumptech.glide.request.RequestListener
import com.bumptech.glide.request.target.Target
import com.example.lunaupload.R
import com.example.lunaupload.databinding.ItemHistoryBinding
import com.example.lunaupload.ui.history.Item

class HistoryAdapter : RecyclerView.Adapter<HistoryAdapter.HistoryViewHolder>() {

    private val items = mutableListOf<Item>()

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): HistoryViewHolder {
        val binding = ItemHistoryBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return HistoryViewHolder(binding)
    }

    override fun onBindViewHolder(holder: HistoryViewHolder, position: Int) {
        val item = items[position]
        holder.bind(item)
    }

    override fun getItemCount(): Int = items.size

    fun setItems(newItems: List<Item>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    class HistoryViewHolder(private val binding: ItemHistoryBinding) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: Item) {
            try {
                // Debugging - Log the URL
                Log.d("HistoryAdapter", "Loading image URL: ${item.imageUrl}")

                // Bind text with null check
                binding.textView.text = item.text ?: "No text available"

                // Load image with Glide and handle errors
                Glide.with(binding.imageView.context)
                    .load(item.imageUrl)
                    .listener(object : RequestListener<android.graphics.drawable.Drawable> {
                        override fun onLoadFailed(
                            e: GlideException?,
                            model: Any?,
                            target: Target<android.graphics.drawable.Drawable>?,
                            isFirstResource: Boolean
                        ): Boolean {
                            Log.e("HistoryAdapter", "Image load failed", e)
                            return false // Allows the error drawable to be set
                        }

                        override fun onResourceReady(
                            resource: android.graphics.drawable.Drawable?,
                            model: Any?,
                            target: Target<android.graphics.drawable.Drawable>?,
                            dataSource: com.bumptech.glide.load.DataSource?,
                            isFirstResource: Boolean
                        ): Boolean {
                            Log.d("HistoryAdapter", "Image loaded successfully")
                            return false // Let Glide handle the resource
                        }
                    })
                    .placeholder(R.drawable.ic_launcher_background)
                    .error(R.drawable.ic_home_black_24dp)
                    .into(binding.imageView)
            } catch (e: Exception) {
                // Handle exceptions during binding
                Log.e("HistoryAdapter", "Error binding item: ${item}", e)
                binding.textView.text = "Error loading item"
                binding.imageView.setImageResource(R.drawable.ic_home_black_24dp)
            }
        }
    }
}
