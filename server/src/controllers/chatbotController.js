const path = require('path');  // 경로 조작을 위한 모듈
const pool = require('../config/database'); // 데이터베이스 연결 모듈 가져오기
const { spawn } = require('child_process');

let pythonProcess = null; // 파이썬 프로세스를 글로벌 변수로 설정하여 계속 실행 상태 유지

// Python 프로세스를 시작하는 함수
function startPythonProcess() {
  if (!pythonProcess) {
    const pythonScriptPath = path.join(__dirname, '../algorithm/script/unified_script.py');
    pythonProcess = spawn('python', [pythonScriptPath]);

    let return_query_error = '';

    // 파이썬 에러 로그 출력
    pythonProcess.stderr.on('data', (error) => {
      return_query_error += error.toString();
      console.error('에러 코드: PY_001 - Python 에러:', return_query_error);
    });

    // 파이썬 프로세스가 종료되면 다시 시작
    pythonProcess.on('close', (code) => {
      console.log(`Python 프로세스가 종료되었습니다. 코드: ${code}`);
      startPythonProcess();
    });
    console.log('Python process start');
  } else {
    console.log("Python 프로세스가 이미 실행 중입니다.");
  }
}

// GET 처리 함수
const getChatList = async (req, res) => {
  const user_id = req.session.userId; // 세션에서 userId 가져오기
  if (!user_id) {
    console.error('에러 코드: AUTH_001 - 인증되지 않은 접근 시도');
    return res.status(401).json({ error: '인증되지 않은 접근입니다.', code: 'AUTH_001' }); // 사용자 인증 실패
  }

  try {
    
    const result = await pool.query(`
      SELECT cb_id, user_id, cb_text, cb_division
      FROM tb_chat_bot
      WHERE user_id = ?
      ORDER BY cb_id DESC;`, [user_id]);

    const chatList = result.map(row => ({
      id: row.cb_id,  // 프론트에서 사용할 cb_id 추가
      text: row.cb_text,
      type: row.cb_division === 0 ? 'bot' : 'user'
    }));

    res.json(chatList);
  } catch (error) {
    console.error('에러 코드: DB_001 - 채팅 기록 가져오기 실패:', error);
    res.status(500).json({ error: '서버 내부 오류', code: 'DB_001' });
  }
};


// POST 처리 함수
const postChatbotData = async (req, res) => {
  const { message } = req.body;
  const user_id = req.session.userId;

  if (!user_id) {
    console.error('에러 코드: AUTH_002 - 인증되지 않은 접근 시도');
    return res.status(401).json({ error: '사용자 인증 오류', code: 'AUTH_002' });
  }

  try {
    // 첫 번째 INSERT: 기본 데이터 저장
    await pool.query(`
      INSERT INTO tb_chat_bot (user_id, cb_text, cb_query, cb_division)
      VALUES (?, ?, ?, ?);
    `, [user_id, message, null, 1]);

    if (message !== '!help') {

      // Python 프로세스에 message와 user_id를 JSON 형식으로 전달
      const inputData_fir = JSON.stringify({ message, user_id });

      // JSON 데이터를 파이썬 프로세스에 전달
      pythonProcess.stdin.write(`${inputData_fir}\n`);
      let return_query_data = '';

      // Python stdout으로부터 데이터를 읽음
      pythonProcess.stdout.once('data', async (data) => {
        return_query_data += data.toString('utf8');
        if (!return_query_data) {
          res.json({ data: '질문 의도를 파악하지 못했습니다. \n 다시 질문해주세요.' });
          return;
        }
        
        // <END>가 있는지 확인하여 끝에 도달했는지 확인
        if (return_query_data.includes("<END>")) {
          return_query_data = return_query_data.replace("<END>", "");  // <END> 구분자를 제거
          
          try {
            const parsedData = JSON.parse(return_query_data);  // Python에서 전달받은 데이터를 JSON으로 파싱
            
            let return_message_data = '';  // 최종 결과 저장 변수
            let executedQueries = [];  // 실행된 쿼리 목록을 저장할 배열
            let queryResult = null;

            // 파싱된 데이터를 key와 query로 분리하여 처리 // [변경사항]예외처리
            for (const [key, query] of Object.entries(parsedData)) {
              
              if (key.includes("예외") || key.includes("링크") || key.toUpperCase().includes("FAQ") || key.toUpperCase().includes("증시")) {
                queryResult = query;
                executedQueries.push(query);  // 실행된 쿼리를 기록
              } else {
                // 각 쿼리 실행
                queryResult = await pool.query(query);
                executedQueries.push(query);  // 실행된 쿼리를 기록
              }

              if (!queryResult) {
                res.json({ data: '질문 의도를 파악하지 못했습니다. \n다시 질문해주세요.' })
              }

              // Python에 전달할 데이터를 JSON으로 구성
              const inputData_sec = JSON.stringify({ key, queryResult });

              // Python 프로세스에 쿼리 결과 전달
              pythonProcess.stdin.write(`${inputData_sec}\n`);

              // 파이썬에서 최종 메시지를 수신
              const finalMessage = await new Promise((resolve) => {
                pythonProcess.stdout.once('data', (data) => {
                  resolve(data.toString('utf8'));
                });
              });

              // 각 결과를 누적하여 최종 메시지로 연결
              return_message_data += finalMessage.trim() + '\n\n';
            }

            // 마지막에 누적된 메시지와 실행된 쿼리들을 DB에 저장
            try {
              await pool.query(`
                INSERT INTO tb_chat_bot (user_id, cb_text, cb_query, cb_division)
                VALUES (?, ?, ?, ?);
              `, [user_id, JSON.parse(return_message_data.trim()), JSON.stringify(executedQueries), 0]);
              } catch (error) {
                await pool.query(`
                  INSERT INTO tb_chat_bot (user_id, cb_text, cb_query, cb_division)
                  VALUES (?, ?, ?, ?);
                `, [user_id, return_message_data.trim(), JSON.stringify(executedQueries), 0]);
              }
            // 모든 쿼리 실행 후 최종 결과 반환
            const newChatIdResult = await pool.query(`
              SELECT cb_id
              FROM tb_chat_bot
              WHERE user_id = ?
              ORDER BY cb_id DESC
              LIMIT 1;
            `, [user_id]);

            const newChatId = newChatIdResult[0].cb_id;

            // 최종 결과를 클라이언트에 전달
            if (return_message_data.includes("\\u")) {
              return_message_data = JSON.parse(return_message_data.trim());
            }
            res.json({ data: return_message_data.trim(), newChatId });

            // --- 모든 변수 초기화 ---
            return_message_data = '';
            executedQueries = [];
            queryResult = null;
            return_query_data = '';

          } catch (error) {
            console.error('에러 코드: PROC_001 - 챗봇 데이터 처리 중 에러:', error);
            res.status(500).json({ error: '서버 내부 오류', code: 'PROC_001' });
          }
        } else {
          console.error('에러 코드: PROC_002 - 챗봇 데이터 처리 중 에러:', return_query_data);
          res.status(500).json({ error: '서버 내부 오류', code: 'PROC_002' });
        }
      });
    } else {
      return_message_data = '안녕하세요. <br /><br />MAP beta ver 0.1 챗봇 서비스는 <br /><br />현재 재무현황과 주가 관련 정보만을 제공하고 있으며, <br /><br />한 문장에 한 가지 질문에 대해서만 답변이 가능합니다. <br /><br />이부분 유의하여 이용 부탁드립니다. <br /><br />감사합니다. ( _ _ )';
      executedQueries = '';
      try {
        await pool.query(`
          INSERT INTO tb_chat_bot (user_id, cb_text, cb_query, cb_division)
          VALUES (?, ?, ?, ?);
        `, [user_id, JSON.parse(return_message_data.trim()), JSON.stringify(executedQueries), 0]);
        } catch (error) {
          await pool.query(`
            INSERT INTO tb_chat_bot (user_id, cb_text, cb_query, cb_division)
            VALUES (?, ?, ?, ?);
          `, [user_id, return_message_data.trim(), JSON.stringify(executedQueries), 0]);
        }

      const newChatIdResult = await pool.query(`
        SELECT cb_id
        FROM tb_chat_bot
        WHERE user_id = ?
        ORDER BY cb_id DESC
        LIMIT 1;
      `, [user_id]);

      const newChatId = newChatIdResult[0].cb_id;

      // 최종 결과를 클라이언트에 전달
      if (return_message_data.includes("\\u")) {
        return_message_data = JSON.parse(return_message_data.trim());
      }
      res.json({ data: return_message_data.trim(), newChatId });

      // --- 모든 변수 초기화 ---
      return_message_data = '';
      executedQueries = [];
      queryResult = null;
      return_query_data = '';


    }
  } catch (error) {
    console.error('에러 코드: DB_003 - 챗봇 데이터 처리 중 데이터베이스 에러:', error);
    res.status(500).json({ error: '서버 내부 오류', code: 'DB_003' });
  }
};

// GET Chat Detail 함수
const getChatDetail = async (req, res) => {
  const { chatId } = req.params;  // URL에서 chatId 추출
  try {
    const result = await pool.query('SELECT cb_text FROM tb_chat_bot WHERE cb_id = ?', [chatId]);
    if (result.length > 0) {
      res.json(result[0]);  // 성공적으로 데이터 반환
    } else {
      res.status(404).json({ error: 'Chat not found' });
    }
  } catch (error) {
    console.error('DB 에러:', error);
    res.status(500).json({ error: '서버 내부 오류' });
  }
};



module.exports = {
  postChatbotData,
  getChatList,
  getChatDetail,
  startPythonProcess,
};