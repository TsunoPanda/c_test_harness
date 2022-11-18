if not exist .\\CovrageReport mkdir .\\CovrageReport
gcovr -r ../ --html-details --output=./CovrageReport/index.html
gcovr -r ../  --txt --output=./CovrageReport/result.txt
