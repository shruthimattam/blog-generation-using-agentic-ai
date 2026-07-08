Get a free key at [console.groq.com](https://console.groq.com/).

### 5. Run the pipeline
```bash
python blogboard/run.py
```
Generates a new blog post, saved under `local_storage/blogs/`.

### 6. Launch the dashboard
```bash
streamlit run app_streamlit.py
```
Open the URL shown in your terminal to trigger generation and browse posts.

## Acknowledgements

Original multi-agent architecture and prompt design by [KalyanM45](https://github.com/KalyanM45/Multi-Agentic-Blog-Generation). This version focuses on making the project runnable without cloud dependencies and adding a browser-based dashboard.

## License

Licensed under the [MIT License](https://opensource.org/licenses/MIT).