# fd --no-ignore --hidden | tree --fromfile > all_tree.txt
# fd | tree --fromfile > selected_tree.txt
# diff -y all_tree.txt selected_tree.txt > diff_tree.txt

fd --no-ignore --hidden | tree --fromfile -J > visual_file_selector_by_ignore_rules/all_tree.json
fd | tree --fromfile -J > visual_file_selector_by_ignore_rules/selected_tree.json
