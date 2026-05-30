const buildExcel = (excelName = '', excelConfig = [], excelData = []) => {
  console.log('excelConfig:', excelConfig);
  excelConfig = excelConfig.filter((i) => {
    return i.type !== 'multiple' && i.colKey !== 'op';
  });
  if (!excelConfig.length || !excelData.length) {
    return;
  }

  const excelHTML =
    '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"> <meta http-equiv="content-type" content="application/msexcel; charset=UTF-8"> <head> <!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>Sheet0</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--> </head> <body>{table}</body> </html>';

  // content="application/msexcel
  // content="application/vnd.ms-excel
  // application/msexcel

  const data = excelData;
  const table = document.createElement('table');
  table.style.display = 'none';

  const tbody = document.createElement('tbody');

  const tr = document.createElement('tr');
  tr.style.backgroundColor = '#ddd';
  const thead = document.createElement('thead');

  excelConfig.forEach((config) => {
    const th = document.createElement('th');
    // th.style = "mso-number-format:'@'";
    th.setAttribute('style', "mso-number-format:'@'");
    th.innerHTML = config.title;
    tr.appendChild(th);
    // thStr += "<th style=\"mso-number-format:'\@'\">" + th + "</th>";
  });
  thead.appendChild(tr);
  table.appendChild(thead);
  data.forEach((trData, index) => {
    const tr = document.createElement('tr');
    excelConfig.forEach((config) => {
      // tr
      const td = document.createElement('td');
      td.setAttribute('style', "mso-number-format:'@'");
      const key = config.colKey;
      let tdData = trData[key] === undefined ? '' : JSON.parse(JSON.stringify(trData[key]));
      if (Object.prototype.toString.call(config.render) === '[object Function]') {
        const kk = config.render(tdData, trData, index);
        const k = String(kk);
        // tdStr += "<td style=\"mso-number-format:'\@'\">" + k + "</td>";
        td.innerHTML = k;
        tr.appendChild(td);
      } else {
        if (tdData === undefined || tdData === null) {
          tdData = '';
        }
        // tdStr += "<td style=\"mso-number-format:'\@'\">" + tdData + "</td>";
        td.innerHTML = tdData;
        tr.appendChild(td);
      }
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  // var a = $('<a id="_cssssw"></a>')
  const a = document.createElement('a');
  a.setAttribute('id', '_cssssw');

  document.body.appendChild(table);
  document.body.appendChild(a);
  const thisExcelHTML = excelHTML.replace(/{(\w+)}/g, table.outerHTML);
  const blob = new Blob([thisExcelHTML], {
    type: 'application/vnd.ms-excel',
  }); // excel blob

  const href = URL.createObjectURL(blob); // 创建对象超链接
  const element = document.getElementById('_cssssw') as HTMLAnchorElement;
  element.href = href; // 绑定a标签
  element.setAttribute('download', `${excelName}.xls`);
  element.click(); // 模拟点击实现下载

  table.parentNode.removeChild(table);
  a.parentNode.removeChild(a);
};

/**
 * 生产Excel 函数
 * 1.参数 config
 * 2.excelName   导出文件名称
 * 3.excelConfig 渲染配置
 * 4.excelData   渲染数据
 */
export const exportExcel = buildExcel;
