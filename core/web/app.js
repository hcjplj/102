// ---- 블록 색상 ----
const C = { cond: 250, date: 190, program: 330, excel: 160, loop: 120, type: 210, key: 20, wait: 45, macro: 290, value: 65 };

function btnImg(label, w, fill) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="24"><rect width="${w}" height="24" rx="5" fill="${fill}"/>` +
    `<text x="${w / 2}" y="16" font-size="12" font-family="Malgun Gothic,sans-serif" fill="#fff" text-anchor="middle">${label}</text></svg>`;
  return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
}
const api = () => (window.pywebview && window.pywebview.api) || null;
function needApp() {
  onStatus('index.html 을 직접 연 상태입니다. 터미널에서 python main.py 로 실행해야 녹화/실행/파일 찾기가 동작해요.', 'err');
}

// 경로 칸: 블록에는 파일 이름만 보여 주고, 값은 전체 경로를 유지한다. (클릭하면 전체 경로 편집, 마우스를 올리면 전체 경로 표시)
class PathField extends Blockly.FieldTextInput {
  constructor() {
    super('');
    this.setTooltip(() => String(this.getValue() || ''));
  }
  getDisplayText_() {
    const name = String(this.getValue() || '').replace(/"/g, '').split(/[\\/]/).pop();
    if (!name) return super.getDisplayText_();
    const shown = name.length > 28 ? name.slice(0, 26) + '…' : name;
    return shown.replace(/\s/g, ' ');
  }
}

// ---- 문장 블록 ----
Blockly.Blocks['open_website'] = {
  init() {
    this.appendValueInput('URL').setCheck(null).appendField('웹사이트 열기');
    this.appendDummyInput().appendField('연 뒤')
      .appendField(new Blockly.FieldNumber(3, 0, 600, 0.5), 'WAIT').appendField('초 기다림');
    this.setInputsInline(true);
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setColour(C.program);
    this.setTooltip('주소(텍스트 블록)를 기본 브라우저로 엽니다. https:// 를 안 써도 됩니다. 페이지가 뜰 때까지 기다리는 시간을 정하세요.');
  },
};

Blockly.Blocks['open_program'] = {
  init() {
    this.appendDummyInput().appendField('프로그램 열기')
      .appendField(new PathField(), 'PATH')
      .appendField(new Blockly.FieldImage(btnImg('찾기', 44, '#8a3b73'), 44, 24, '찾기', () => {
        if (!api()) return needApp();
        api().pick_program().then((p) => { if (p) this.setFieldValue(p, 'PATH'); });
      }));
    this.appendDummyInput().appendField('연 뒤')
      .appendField(new Blockly.FieldNumber(3, 0, 600, 0.5), 'WAIT').appendField('초 기다림');
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setColour(C.program);
    this.setTooltip('exe, bat, 바로가기 파일을 실행합니다. 프로그램 창이 뜰 때까지 기다리는 시간을 정하세요.');
  },
};

Blockly.Blocks['excel_each'] = {
  init() {
    this.appendDummyInput().appendField('엑셀 파일')
      .appendField(new PathField(), 'FILE')
      .appendField(new Blockly.FieldImage(btnImg('찾기', 44, '#1e7a4c'), 44, 24, '찾기', () => {
        if (!api()) return needApp();
        api().pick_file().then((p) => { if (p) this.setFieldValue(p, 'FILE'); });
      }));
    this.appendDummyInput()
      .appendField(new Blockly.FieldTextInput('Sheet1'), 'SHEET')
      .appendField('시트')
      .appendField(new Blockly.FieldTextInput('A', (v) => v.toUpperCase().replace(/[^A-Z]/g, '') || null), 'COL')
      .appendField('열')
      .appendField(new Blockly.FieldNumber(2, 1, 1048576, 1), 'START')
      .appendField('행');
    this.appendStatementInput('DO').appendField('각 줄마다 실행');
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setColour(C.excel);
    this.setTooltip("엑셀을 한 줄씩 내려가며 안쪽 블록을 실행합니다. 시트(비우거나 이름이 없으면 첫 시트), 열(가져올 열), 행(시작 행)을 정하세요. '열'의 값이 줄마다 [엑셀 값] 블록으로 나옵니다.");
  },
};

Blockly.Blocks['repeat_times'] = {
  init() {
    this.appendDummyInput().appendField('반복')
      .appendField(new Blockly.FieldNumber(10, 1, 100000, 1), 'TIMES').appendField('번');
    this.appendStatementInput('DO').appendField('실행');
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setColour(C.loop);
    this.setTooltip('안쪽 블록을 정한 횟수만큼 반복합니다.');
  },
};

Blockly.Blocks['repeat_forever'] = {
  init() {
    this.appendDummyInput().appendField('계속 반복 (ESC 로 멈출 때까지)');
    this.appendStatementInput('DO').appendField('실행');
    this.setPreviousStatement(true);
    this.setColour(C.loop);
    this.setTooltip('멈출 때까지 안쪽 블록을 계속 반복합니다. 실행 중 ESC 를 누르면 멈춥니다.');
  },
};

Blockly.Blocks['type_text'] = {
  init() {
    this.appendValueInput('TEXT').appendField('타이핑');
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setInputsInline(true);
    this.setColour(C.type);
    this.setTooltip('끼워 넣은 값을 복사해서 현재 커서 위치에 붙여넣습니다. 한글도 깨지지 않아요. (실행 후 원래 클립보드 내용은 되돌립니다)');
  },
};

Blockly.Blocks['key_press'] = {
  init() {
    this.appendDummyInput().appendField('특수키')
      .appendField(new Blockly.FieldDropdown([
        ['Enter', 'enter'], ['Tab', 'tab'], ['Delete', 'delete'], ['Backspace', 'backspace'],
        ['아래 화살표', 'down'], ['위 화살표', 'up'], ['왼쪽 화살표', 'left'], ['오른쪽 화살표', 'right'],
      ]), 'KEY');
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setColour(C.key);
  },
};

Blockly.Blocks['wait'] = {
  init() {
    this.appendDummyInput().appendField('대기')
      .appendField(new Blockly.FieldNumber(1, 0, 3600, 0.1), 'SEC').appendField('초');
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setColour(C.wait);
  },
};

Blockly.Blocks['macro_play'] = {
  init() {
    this.events = [];
    this.appendDummyInput().appendField('녹화 실행')
      .appendField(new Blockly.FieldLabel('이벤트 0개'), 'INFO');
    this.appendDummyInput()
      .appendField(new Blockly.FieldImage(btnImg('녹화', 60, '#d6392f'), 60, 24, '녹화', () => {
        if (!api()) return needApp();
        api().record_macro().then((ev) => this.setEvents(ev));
      }))
      .appendField(new Blockly.FieldImage(btnImg('테스트', 70, '#3a7bd5'), 70, 24, '테스트', () => {
        if (!api()) return needApp();
        if (this.events.length) api().play_macro(this.events);
      }));
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setColour(C.macro);
    this.setTooltip('마우스/키보드 동작을 녹화(pynput)해서 그대로 재생합니다. 녹화 종료는 ESC.');
  },
  setEvents(ev) {
    this.events = ev || [];
    this.getField('INFO').setValue(`이벤트 ${this.events.length}개`);
  },
  saveExtraState() { return { events: this.events }; },
  loadExtraState(s) { this.setEvents(s.events); },
};

// ---- 값 블록 ----
function insideExcel(block) {
  for (let p = block.getSurroundParent(); p; p = p.getSurroundParent()) if (p.type === 'excel_each') return true;
  return false;
}
// 엑셀 블록 밖에 놓이면 회색으로 흐리게 보여서 알아차리게 한다.
function dimIfOutside(block) {
  if (!block.workspace || block.isInFlyout) return;
  block.setColour(insideExcel(block) ? C.value : '#9aa0a6');
}

Blockly.Blocks['excel_value'] = {
  init() {
    this.appendDummyInput().appendField('엑셀 값');
    this.setOutput(true);
    this.setColour(C.value);
    this.setTooltip("엑셀 블록의 '열'에서, 지금 줄의 값을 순서대로 돌려줍니다. 엑셀 블록 안에 있어야 색이 살아납니다.");
  },
  onchange() { dimIfOutside(this); },
};

Blockly.Blocks['excel_row_no'] = {
  init() {
    this.appendDummyInput().appendField('엑셀 줄 번호');
    this.setOutput(true);
    this.setColour(C.value);
    this.setTooltip("'엑셀 각 줄마다 실행' 블록 안에서, 지금 처리 중인 엑셀 줄 번호를 돌려줍니다.");
  },
  onchange() { dimIfOutside(this); },
};

// ---- 날짜 / 시간 ----
const DAYS_KO = '일월화수목금토';
// 엑셀 방식 형식(yyyy, MM, dd, HH, mm, ss, E, a ...)으로 예시 글자를 만든다. (드롭다운에 오늘 날짜로 미리 보여 주기 위함)
function fmtExample(d, fmt) {
  const p = (n, w = 2) => String(n).padStart(w, '0');
  const h12 = d.getHours() % 12 || 12;
  return fmt.replace(/yyyy|yy|MM|M|dd|d|HH|H|hh|h|mm|m|ss|s|EEEE|E|a/g, (t) => ({
    yyyy: p(d.getFullYear(), 4), yy: p(d.getFullYear() % 100), MM: p(d.getMonth() + 1), M: d.getMonth() + 1,
    dd: p(d.getDate()), d: d.getDate(), HH: p(d.getHours()), H: d.getHours(), hh: p(h12), h: h12,
    mm: p(d.getMinutes()), m: d.getMinutes(), ss: p(d.getSeconds()), s: d.getSeconds(),
    E: DAYS_KO[d.getDay()], EEEE: DAYS_KO[d.getDay()] + '요일', a: d.getHours() < 12 ? '오전' : '오후',
  }[t]));
}
const DATE_FORMATS = ['yyyy-MM-dd', 'yyyy.MM.dd', 'yyyyMMdd', 'yyMMdd', 'yy-MM-dd', 'yy.MM.dd', 'yyyy/MM/dd',
  'yyyy년 M월 d일', 'yyyy년 MM월 dd일', 'M월 d일', 'yyyy-MM-dd (E)', 'yyyy-MM-dd EEEE'];
const TIME_FORMATS = ['HH:mm', 'HH:mm:ss', 'HHmm', 'HHmmss', 'a h:mm', 'H시 m분', 'HH'];

function formatDropdown(formats) {
  return new Blockly.FieldDropdown(() => {
    const now = new Date();
    return [...formats.map((f) => [fmtExample(now, f), f]), ['직접 입력', 'custom']];
  }, function (v) {  // 직접 입력일 때만 입력칸을 보여 준다
    const b = this.getSourceBlock();
    const c = b && b.getField('CUSTOM');
    if (c) c.setVisible(v === 'custom');
    return v;
  });
}

const SIGNS = [['+', '+'], ['-', '-']];
const DATE_UNITS = [['일', 'day'], ['주', 'week'], ['개월', 'month'], ['년', 'year'], ['영업일', 'bday']];
const TIME_UNITS = [['시간', 'hour'], ['분', 'minute'], ['초', 'second']];

// 날짜/시간 블록 오른쪽 끝에 가로로 계속 이어 붙일 수 있는 [+/- 숫자 단위] 조정 블록
function defineAdjustBlock(type, kind, units, defUnit, tip) {
  Blockly.Blocks[type] = {
    init() {
      this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown(SIGNS), 'SIGN')
        .appendField(new Blockly.FieldNumber(1, 0, 100000, 1), 'OFFSET')
        .appendField(new Blockly.FieldDropdown(units), 'UNIT');
      this.getField('UNIT').setValue(defUnit);
      this.appendValueInput('NEXT').setCheck(kind);
      this.setInputsInline(true);
      this.setOutput(true, kind);
      this.setColour(C.date);
      this.setTooltip(tip);
    },
  };
}

function defineDateTimeBlock(type, label, base, formats, defFmt, units, defUnit, kind, tip) {
  Blockly.Blocks[type] = {
    init() {
      this.appendDummyInput().appendField(label)
        .appendField(formatDropdown(formats), 'FMT')
        .appendField(new Blockly.FieldTextInput(defFmt), 'CUSTOM')
        .appendField(base)
        .appendField(new Blockly.FieldDropdown(SIGNS), 'SIGN')
        .appendField(new Blockly.FieldNumber(0, 0, 100000, 1), 'OFFSET')
        .appendField(new Blockly.FieldDropdown(units), 'UNIT');
      this.appendValueInput('ADJ').setCheck(kind);  // 오른쪽에 조정 블록을 가로로 이어 붙이는 자리
      this.setInputsInline(true);
      this.getField('FMT').setValue(defFmt);
      this.getField('CUSTOM').setVisible(false);
      this.getField('UNIT').setValue(defUnit);
      this.setOutput(true);
      this.setColour(C.date);
      this.setTooltip(tip);
    },
  };
}
defineDateTimeBlock('date_value', '날짜', '오늘', DATE_FORMATS, 'yyyy-MM-dd', DATE_UNITS, 'day', 'DateAdjust',
  "오늘 날짜를 고른 형식으로 돌려줍니다. [+/- 숫자 단위]로 더하고 뺍니다. (예: + 1 일 = 내일) " +
  "오른쪽에 [날짜 조정] 블록을 가로로 더 이어 붙이면 왼쪽부터 차례로 계산합니다. " +
  "'영업일'은 토/일과 '휴일 설정' 블록의 휴일을 건너뜁니다. 직접 입력은 yyyy, yy, MM, dd, E(요일) 를 씁니다.");
defineDateTimeBlock('time_value', '시간', '지금', TIME_FORMATS, 'HH:mm', TIME_UNITS, 'hour', 'TimeAdjust',
  "지금 시각을 고른 형식으로 돌려줍니다. [+/- 숫자 단위]로 더하고 뺍니다. (예: 13시 + 1 시간 = 14시, 23시 + 1 시간 = 0시) " +
  "오른쪽에 [시간 조정] 블록을 가로로 더 이어 붙일 수 있습니다. 직접 입력은 HH, H, mm, ss, a(오전/오후) 를 씁니다.");
defineAdjustBlock('date_adjust', 'DateAdjust', DATE_UNITS, 'day', '날짜 블록 오른쪽에 이어 붙여서 더하거나 뺍니다. 왼쪽부터 차례로 계산합니다. (예: + 1 개월  - 1 일 = 한 달 뒤의 전날)');
defineAdjustBlock('time_adjust', 'TimeAdjust', TIME_UNITS, 'hour', '시간 블록 오른쪽에 이어 붙여서 더하거나 뺍니다. 왼쪽부터 차례로 계산합니다.');

// 연결하지 않고 작업 영역 아무 곳에나 놓는 설정 블록. 안쪽에 [휴일 날짜]/[휴일 기간] 블록을 이어 붙인다.
Blockly.Blocks['holiday_settings'] = {
  init() {
    this.appendDummyInput().appendField('휴일 설정 (연결하지 않고 아무 곳에나 두세요)');
    this.appendDummyInput()
      .appendField(new Blockly.FieldCheckbox('TRUE'), 'SAT').appendField('토요일 휴무')
      .appendField(new Blockly.FieldCheckbox('TRUE'), 'SUN').appendField('일요일 휴무');
    this.appendStatementInput('DATES').appendField('추가 휴일');
    this.setColour(C.date);
    this.setTooltip("'날짜' 블록의 영업일 계산에 쓰는 휴일입니다. 안쪽에 [휴일 날짜], [휴일 기간] 블록을 이어 붙이세요.");
  },
};

function insideHoliday(block) {
  for (let p = block.getSurroundParent(); p; p = p.getSurroundParent()) if (p.type === 'holiday_settings') return true;
  return false;
}
function ymdFields(input, prefix, d) {
  input.appendField(new Blockly.FieldNumber(d.getFullYear(), 1900, 2200, 1), prefix + 'YEAR').appendField('년')
    .appendField(new Blockly.FieldNumber(d.getMonth() + 1, 1, 12, 1), prefix + 'MONTH').appendField('월')
    .appendField(new Blockly.FieldNumber(d.getDate(), 1, 31, 1), prefix + 'DAY').appendField('일');
}
Blockly.Blocks['holiday_date'] = {
  init() {
    ymdFields(this.appendDummyInput().appendField('휴일'), '', new Date());
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setColour(C.date);
    this.setTooltip("쉬는 날 하루입니다. '휴일 설정' 블록 안에 이어 붙이세요.");
  },
  onchange() { if (this.workspace && !this.isInFlyout) this.setColour(insideHoliday(this) ? C.date : '#9aa0a6'); },
};
Blockly.Blocks['holiday_range'] = {
  init() {
    ymdFields(this.appendDummyInput().appendField('휴일 기간  시작'), 'S_', new Date());
    ymdFields(this.appendDummyInput().appendField('끝').appendField('       '), 'E_', new Date());
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setColour(C.date);
    this.setTooltip("연휴처럼 이어진 쉬는 날입니다. 시작일과 끝일을 모두 쉬는 날로 칩니다. '휴일 설정' 블록 안에 이어 붙이세요.");
  },
  onchange() { if (this.workspace && !this.isInFlyout) this.setColour(insideHoliday(this) ? C.date : '#9aa0a6'); },
};

// ---- 조건 (if) ----
Blockly.Blocks['if_else'] = {
  init() {
    this.appendValueInput('COND').setCheck('Boolean').appendField('만약');
    this.appendStatementInput('DO').appendField('이면 실행');
    this.appendStatementInput('ELSE').appendField('아니면 실행');
    this.setPreviousStatement(true); this.setNextStatement(true);
    this.setColour(C.cond);
    this.setTooltip('조건이 맞으면 [이면 실행] 안의 블록을, 아니면 [아니면 실행] 안의 블록을 실행합니다. 아니면 칸은 비워 둬도 됩니다.');
  },
};

Blockly.Blocks['cond_bday'] = {
  init() {
    this.appendDummyInput().appendField('날짜 오늘')
      .appendField(new Blockly.FieldDropdown(SIGNS), 'SIGN')
      .appendField(new Blockly.FieldNumber(0, 0, 100000, 1), 'OFFSET')
      .appendField(new Blockly.FieldDropdown(DATE_UNITS.filter((u) => u[1] !== 'bday')), 'UNIT');
    this.appendValueInput('ADJ').setCheck('DateAdjust');
    this.appendDummyInput().appendField('이(가) 영업일');
    this.setInputsInline(true);
    this.setOutput(true, 'Boolean');
    this.setColour(C.cond);
    this.setTooltip("토/일과 '휴일 설정' 블록의 휴일이 아니면 맞음(영업일)입니다. 오늘 0 일 = 오늘이 영업일인지, + 1 일 = 내일이 영업일인지 확인합니다. 휴일 설정 블록이 없으면 토/일만 쉬는 날로 봅니다.");
  },
};

Blockly.Blocks['cond_compare'] = {
  init() {
    this.appendValueInput('A');
    this.appendDummyInput().appendField(new Blockly.FieldDropdown([
      ['=', 'EQ'], ['≠', 'NEQ'], ['>', 'GT'], ['≥', 'GTE'], ['<', 'LT'], ['≤', 'LTE']]), 'OP');
    this.appendValueInput('B');
    this.setInputsInline(true);
    this.setOutput(true, 'Boolean');
    this.setColour(C.cond);
    this.setTooltip('두 값을 비교합니다. 둘 다 숫자면 숫자로, 아니면 글자로 비교합니다. (앞뒤 공백은 무시)');
  },
};

Blockly.Blocks['cond_logic'] = {
  init() {
    this.appendValueInput('A').setCheck('Boolean');
    this.appendDummyInput().appendField(new Blockly.FieldDropdown([['그리고', 'AND'], ['또는', 'OR']]), 'OP');
    this.appendValueInput('B').setCheck('Boolean');
    this.setInputsInline(true);
    this.setOutput(true, 'Boolean');
    this.setColour(C.cond);
    this.setTooltip('그리고: 둘 다 맞아야 맞음 / 또는: 하나라도 맞으면 맞음');
  },
};

Blockly.Blocks['cond_not'] = {
  init() {
    this.appendValueInput('A').setCheck('Boolean').appendField('아니다');
    this.setInputsInline(true);
    this.setOutput(true, 'Boolean');
    this.setColour(C.cond);
    this.setTooltip('조건을 뒤집습니다. (영업일이 아니면 = 아니다 + 영업일 조건)');
  },
};

Blockly.Blocks['cond_empty'] = {
  init() {
    this.appendValueInput('A');
    this.appendDummyInput().appendField('이(가) 비어 있음');
    this.setInputsInline(true);
    this.setOutput(true, 'Boolean');
    this.setColour(C.cond);
    this.setTooltip('값이 비어 있거나 공백뿐이면 맞음입니다. (예: 엑셀 값이 빈 칸인지 확인)');
  },
};

// ---- 툴박스 ----
const toolbox = {
  kind: 'categoryToolbox',
  contents: [
    { kind: 'category', name: '열기', colour: C.program, contents: [
      { kind: 'block', type: 'open_program' },
      { kind: 'block', type: 'open_website', inputs: { URL: { shadow: { type: 'text', fields: { TEXT: 'https://' } } } } },
    ] },
    { kind: 'category', name: '엑셀', colour: C.excel, contents: [{ kind: 'block', type: 'excel_each' }, { kind: 'block', type: 'excel_value' }, { kind: 'block', type: 'excel_row_no' }] },
    { kind: 'category', name: '반복', colour: C.loop, contents: [{ kind: 'block', type: 'repeat_times' }, { kind: 'block', type: 'repeat_forever' }] },
    { kind: 'category', name: '입력', colour: C.type, contents: [
      { kind: 'block', type: 'type_text' }, { kind: 'block', type: 'key_press' }, { kind: 'block', type: 'wait' },
    ] },
    { kind: 'category', name: '녹화', colour: C.macro, contents: [{ kind: 'block', type: 'macro_play' }] },
    { kind: 'category', name: '조건', colour: C.cond, contents: [
      { kind: 'block', type: 'if_else' },
      { kind: 'block', type: 'cond_bday' },
      { kind: 'block', type: 'cond_compare', inputs: {
        A: { shadow: { type: 'text', fields: { TEXT: '' } } }, B: { shadow: { type: 'text', fields: { TEXT: '' } } } } },
      { kind: 'block', type: 'cond_logic' },
      { kind: 'block', type: 'cond_not' },
      { kind: 'block', type: 'cond_empty', inputs: { A: { shadow: { type: 'text', fields: { TEXT: '' } } } } },
    ] },
    { kind: 'category', name: '날짜', colour: C.date, contents: [
      { kind: 'block', type: 'date_value' }, { kind: 'block', type: 'date_adjust' },
      { kind: 'block', type: 'time_value' }, { kind: 'block', type: 'time_adjust' },
      { kind: 'block', type: 'holiday_settings' },
      { kind: 'block', type: 'holiday_date' }, { kind: 'block', type: 'holiday_range' },
    ] },
    { kind: 'category', name: '값', colour: C.value, contents: [
      { kind: 'block', type: 'text' }, { kind: 'block', type: 'text_join' },
      { kind: 'block', type: 'math_number' },
    ] },
  ],
};

// 내부/외부 입력 전환 메뉴는 숨긴다 (블록 모양을 하나로 통일)
Blockly.ContextMenuRegistry.registry.unregister('blockInline');

const ws = Blockly.inject('blocklyDiv', {
  toolbox,
  grid: { spacing: 20, length: 3, colour: '#d5d9e0', snap: true },
  zoom: { controls: true, wheel: true, startScale: 1.0, minScale: 0.4, maxScale: 2 },
  trashcan: true,
  sounds: false,
});
window.addEventListener('resize', () => Blockly.svgResize(ws));

const SAMPLE = { blocks: { languageVersion: 0, blocks: [{
  type: 'macro_play', x: 40, y: 30,
  next: { block: {
    type: 'excel_each',
    fields: { FILE: '', SHEET: 'Sheet1', START: 2, COL: 'A' },
    inputs: { DO: { block: { type: 'type_text',
      inputs: { TEXT: { block: { type: 'excel_value' } } },
      next: { block: { type: 'key_press', fields: { KEY: 'enter' } } } } } },
  } },
}] } };
Blockly.serialization.workspaces.load(SAMPLE, ws);

// ---- 툴바 / 상태 ----
const $ = (id) => document.getElementById(id);
function onStatus(msg, kind) { const s = $('status'); s.textContent = msg; s.className = kind || ''; }
function onRunState(running) { $('run').disabled = running; $('stop').disabled = !running; }
let hl = null;
function highlight(id) {
  if (hl) { try { hl.setHighlighted(false); } catch (e) {} }
  hl = id ? ws.getBlockById(id) : null;
  if (hl) hl.setHighlighted(true);
}
const state = () => Blockly.serialization.workspaces.save(ws);

$('run').onclick = () => { if (api()) api().run(JSON.stringify(state())); else needApp(); };
$('stop').onclick = () => (api() ? api().stop() : needApp());
$('clear').onclick = () => { if (confirm('모든 블록을 지울까요?')) ws.clear(); };
$('save').onclick = async () => {
  if (!api()) return needApp();
  if (await api().save_project(JSON.stringify(state()))) onStatus('저장했습니다.', 'ok');
};
$('open').onclick = async () => {
  if (!api()) return needApp();
  const text = await api().load_project();
  if (text) { ws.clear(); Blockly.serialization.workspaces.load(JSON.parse(text), ws); onStatus('불러왔습니다.', 'ok'); }
};
