cd /media/root/Prima
cd hexo_blog_demo
cd blog_template
rm -rf node_modules
npm install hexo-generator-search --save
npm install
hexo generate
cd public
python3 -m http.server 8021