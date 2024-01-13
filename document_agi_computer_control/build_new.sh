export HEADLESS=true

bash build_gemini_doc.sh -s 
env PROJECT_NAME="graph-of-thoughts" AUTHOR="spcl" bash build_doc_with_author_and_project_name.sh -s
env PROJECT_NAME="LLM_Tree_Search" AUTHOR="waterhorse1" bash build_doc_with_author_and_project_name.sh -s
bash build_pyjom_doc.sh -s
env PROJECT_NAME="DALLE2-pytorch" AUTHOR="lucidrains" bash build_doc_with_author_and_project_name.sh -s
env PROJECT_NAME="Kacket" AUTHOR="ShorterThanDijkstra" bash build_doc_with_author_and_project_name.sh -s
env PROJECT_NAME="vced" AUTHOR="datawhalechina" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="he4o" AUTHOR="jiaxiaogang" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="gato" AUTHOR="OrigamiDream" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="Voyager" AUTHOR="MineDojo" bash build_doc_at_prima_with_author_and_project_name.sh -s
