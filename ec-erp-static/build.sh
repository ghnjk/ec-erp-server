rm -rf dist
npm run build

rm -rf ../ec-erp-server/static
mv dist ../ec-erp-server/static
