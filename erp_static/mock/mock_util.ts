const fs = require('fs');


class MockUtil {
  /**
   * 从文件中加载json
   * @param filePath
   */
  loadFromJson(filePath: string) {
    const data = fs.readFileSync(filePath, 'utf-8');
    const doc = JSON.parse(data);
    return doc;
  }

  /**
   * 根据url生成mock返回
   * @param apis
   */
  buildMockCases(apis: any []): any [] {
    const cases = [];
    for (let i = 0; i < apis.length; i++) {
      const { url, method } = apis[i];
      cases.push({
        url,
        method,
        response: () => (
          this.loadFromJson('mock/api/data' + url + '.json')
        ),
      });
    }
    return cases;
  }
}

export default new MockUtil();
