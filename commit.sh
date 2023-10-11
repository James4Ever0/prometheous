# for auto commit generation: https://github.com/di-sukharev/opencommit
# obtain free api key: https://github.com/chatanywhere/GPT_API_free
git config --global core.autocrlf input # shall this be builtin, not from here.

git pull origin main
git add .
git commit -m "message"
git push origin main
