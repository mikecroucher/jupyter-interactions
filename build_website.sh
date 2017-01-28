#!/bin/bash
openssl aes-256-cbc -K $encrypted_8e28d6063879_key -iv $encrypted_8e28d6063879_iv -in sage_interactions.enc -out ~/.ssh/publish-key -d
git clone https://github.com/christianp/jupyter-interactions-site
pip install -r jupyter-interactions-site/requirements.txt
cd jupyter-interactions-site
python build_site.py --config=prod
chmod u=rw,og= ~/.ssh/publish-key
echo "Host github.com" >> ~/.ssh/config
echo "  IdentityFile ~/.ssh/publish-key" >> ~/.ssh/config
git remote set-url origin git@github.com:mikecroucher/jupyter-interactions
git fetch origin -f gh-pages:gh-pages
ghp-import -n -p -m "Update gh-pages." ./site
