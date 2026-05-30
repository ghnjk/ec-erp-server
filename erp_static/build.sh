rm -rf dist
npm run build

rm -rf ../static
mv dist ../static
