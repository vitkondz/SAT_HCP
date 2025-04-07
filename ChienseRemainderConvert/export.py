import csv

# Đọc file .txt
with open('logfile.txt', 'r') as infile:
    lines = infile.readlines()

# Ghi ra file .csv
with open('result.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Viết header nếu muốn
    writer.writerow(['Graph', 'K', 'Status', 'Time1', 'Time2', 'Result'])

    # Duyệt qua từng dòng và ghi vào file csv
    for line in lines:
        # Tách bằng bất kỳ số lượng khoảng trắng nào
        row = line.split()
        writer.writerow(row)