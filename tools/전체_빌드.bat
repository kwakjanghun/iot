@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ====================================================
echo   사물인터넷 수업 자료 빌드
echo ====================================================
echo.

echo [1/3] 구글드라이브 수업 홈 메뉴 만들기...
python build_index.py
if errorlevel 1 goto :fail

echo.
echo [2/3] 대본에 영상 붙이기...
python add_video.py
if errorlevel 1 goto :fail

echo.
echo [3/3] 웹사이트용 빌드...
python build_web.py
if errorlevel 1 goto :fail

echo.
echo ====================================================
echo   빌드 완료
echo ====================================================
echo.
echo  로컬  : 구글드라이브 키트 폴더의 index.html
echo  웹    : 아래에서 커밋하면 사이트에 반영됩니다
echo.

cd /d "%~dp0.."
git add -A
git status --short
echo.
set /p YN="지금 GitHub에 올릴까요? (Y/N) "
if /i "%YN%"=="Y" goto :push
echo 올리지 않았습니다. 나중에 이 파일을 다시 실행하세요.
goto :end

:push
git commit -m "수업 자료 업데이트"
git push origin HEAD
echo.
echo  https://kwakjanghun.github.io/iot/ 에 1~2분 뒤 반영됩니다.
goto :end

:fail
echo.
echo  ** 빌드 중 오류가 났습니다. 위 메시지를 확인하세요. **

:end
echo.
pause
