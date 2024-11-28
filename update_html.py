# Updates the HTML of the browser source that, in OBS, shows the username of the person who redeems the item
file_path = 'Tachobuck Stream Integrations\\redeem_event.html'


def update_html_file(user_name):    
    user_name = str(user_name)    
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
          if f'id="redeem-text"' in line:  
            start_index = line.find('>') + 1  
            end_index = line.find('</') 

            lines[i] = line[:start_index] + user_name + line[end_index:]

            break
          
    with open(file_path, 'w') as file:
        file.writelines(lines)

    print("Updated HTML with username: " + str(user_name))

