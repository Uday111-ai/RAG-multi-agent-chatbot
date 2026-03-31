# DocMind Deployment TODO

## ✅ Completed by BLACKBOXAI
- [x] Created `requirements.txt`
- [x] Created `.gitignore`
- [x] Git init + initial commit (next step)

## 🔄 Next Steps (User)
1. **Local Test**: `streamlit run app.py` — ensure works w/ your GROQ_API_KEY in `.env`.

2. **GitHub Repo**:
   ```
   git remote add origin https://github.com/YOUR_USERNAME/docmind-ai.git
   git branch -M main
   git push -u origin main
   ```

3. **Streamlit Cloud Deploy** (1 min):
   - Go to https://share.streamlit.io/
   - "New app" → Connect GitHub repo → Select `app.py` → Deploy.
   - Settings → Secrets: Add `GROQ_API_KEY = your_key`.

4. **Usage**: App restarts fresh (no chroma_db persistence; re-upload PDFs).

**App will be at**: https://your-app-name.streamlit.app

Ping me w/ URL when live!

