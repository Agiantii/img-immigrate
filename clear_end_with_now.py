import os

target_folder = r"E:\temp\new-anote"
def clear_md_end_with_now(target_folder):
    for root,_,files in os.walk(target_folder):
        for file in files:
            if(file.endswith('_now.md')):
                print(file)
                file_path = os.path.join(root,file)
                os.remove(file_path) 
def main():
    clear_md_end_with_now(target_folder)

if __name__ == '__main__':
    main()