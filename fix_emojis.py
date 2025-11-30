file_path = r'templates\dashboard_react.html'

# read as bytes
with open(file_path, 'rb') as f:
    content = f.read()

# emojis got triple-encoded somehow
# need to decode/encode multiple times to fix

try:
    step1 = content.decode('utf-8')
    step2 = step1.encode('latin-1')
    step3 = step2.decode('utf-8')
    step4 = step3.encode('latin-1')
    fixed_text = step4.decode('utf-8')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_text)

    print('Successfully fixed all emojis!')
except Exception as e:
    print(f'Error: {e}')
    print('Trying hex-based replacement instead...')

    # replace bad emoji bytes with good ones
    shield_bad = b'\xc3\x83\xc2\xb0\xc3\x85\xc2\xb8\xc3\xa2\xc2\x80\xc2\xba\xc3\x82\xc2\xa1\xc3\x83\xc2\xaf\xc3\x82\xc2\xb8\xc3\x82\x8f'
    shield_good = b'\xf0\x9f\x9b\xa1\xef\xb8\x8f'

    content = content.replace(shield_bad, shield_good)

    with open(file_path, 'wb') as f:
        f.write(content)
    print('Fixed using binary replacement')
