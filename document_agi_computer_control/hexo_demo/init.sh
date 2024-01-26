# export http_proxy=""
# export https_proxy=""
# export all_proxy=""

# cannot generate blog here. cannot symlink.

cd /media/root/Prima
mkdir hexo_blog_demo
cd hexo_blog_demo

rm -rf blog
hexo init blog
cd blog
git clone https://github.com/wzpan/hexo-theme-freemind.git themes/freemind
npm install hexo-generator-search --save
npm install
hexo new "New blog"
hexo generate
# where is template?
cd public
python3.9 -m http.server 8021