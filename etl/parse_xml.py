import xml.etree.ElementTree as ET  
import json  

def parse_xml_to_json(xml_file, output_file):
    """
    This function reads an XML file containing SMS records
    and converts them into a JSON file.
    """
       
    tree = ET.parse(xml_file)
    root = tree.getroot()
     
    sms_records = []
     
    for sms in root.findall('sms'):
         
        body = sms.get('body', '')
         
        transaction_type = None
        if 'received' in body.lower():
            transaction_type = 'RECEIVED'
        elif 'payment' in body.lower():
            transaction_type = 'PAYMENT'
        elif 'transferred' in body.lower():
            transaction_type = 'TRANSFER'
        elif 'deposit' in body.lower():
            transaction_type = 'DEPOSIT'
        
        
        amount = None
        if 'RWF' in body:
            
            words = body.split()
            for i, word in enumerate(words):
                if 'RWF' in word and i > 0:
                    
                    amount_str = words[i-1].replace(',', '')
                    if amount_str.isdigit():
                        amount = float(amount_str)
                        break
        
        
        sender = None
        if 'from' in body:
            
            start = body.find('from') + 5
            end = body.find('(', start)
            if end > start:
                sender = body[start:end].strip()
        
        
        recipient = None
        if 'to' in body:
            
            start = body.find('to') + 3
            words_after_to = body[start:].split()
            if len(words_after_to) >= 2:
                
                recipient = f"{words_after_to[0]} {words_after_to[1]}"
        
        
        record = {
            'address': sms.get('address'),
            'date': sms.get('date'),
            'readable_date': sms.get('readable_date'),
            'body': body,
            'transaction_type': transaction_type,
            'amount': amount,
            'sender': sender,
            'recipient': recipient,
            'contact_name': sms.get('contact_name')
        }
        
        
        sms_records.append(record)
    

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sms_records, f, indent=2, ensure_ascii=False)
    

    print(f"Successfully parsed {len(sms_records)} SMS records")
    print(f"Output saved to: {output_file}")
    
    return sms_records


if __name__ == "__main__":
    
    xml_file = "modified_sms_v2 (1).xml"
    output_file = "sms_records.json"
    
 
    parse_xml_to_json(xml_file, output_file)
