fd --no-ignore | tree --fromfile >  all_tree.txt
fd | tree --fromfile >selected_tree.txt
diff -y all_tree.txt selected_tree.txt | less