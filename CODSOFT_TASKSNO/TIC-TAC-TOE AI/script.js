const HUMAN = 'X';
const AI = 'O';

let board = Array(9).fill('');
let gameOver = false;
let humanFirst = true;
let scores = { human: 0, ai: 0, draw: 0 };

const WIN_LINES = [
  [0,1,2],[3,4,5],[6,7,8],
  [0,3,6],[1,4,7],[2,5,8],
  [0,4,8],[2,4,6]
];

function checkWinner(b, player) {
  return WIN_LINES.some(([a, c, d]) => b[a] === player && b[c] === player && b[d] === player);
}

function getWinLine(b, player) {
  return WIN_LINES.find(([a, c, d]) => b[a] === player && b[c] === player && b[d] === player);
}

function availableMoves(b) {
  return b.reduce((acc, v, i) => v === '' ? [...acc, i] : acc, []);
}

function minimax(b, isMax, alpha, beta) {
  if (checkWinner(b, AI))    return 1;
  if (checkWinner(b, HUMAN)) return -1;
  const moves = availableMoves(b);
  if (!moves.length) return 0;

  if (isMax) {
    let best = -2;
    for (const m of moves) {
      b[m] = AI;
      best = Math.max(best, minimax(b, false, alpha, beta));
      b[m] = '';
      alpha = Math.max(alpha, best);
      if (beta <= alpha) break;
    }
    return best;
  } else {
    let best = 2;
    for (const m of moves) {
      b[m] = HUMAN;
      best = Math.min(best, minimax(b, true, alpha, beta));
      b[m] = '';
      beta = Math.min(beta, best);
      if (beta <= alpha) break;
    }
    return best;
  }
}

function bestMove(b) {
  let bestScore = -2, move = null;
  for (const m of availableMoves(b)) {
    b[m] = AI;
    const score = minimax(b, false, -2, 2);
    b[m] = '';
    if (score > bestScore) { bestScore = score; move = m; }
  }
  return move;
}

function renderBoard() {
  document.querySelectorAll('.cell').forEach((cell, i) => {
    cell.textContent = board[i];
    cell.className = 'cell';
    if (board[i]) cell.classList.add(board[i].toLowerCase(), 'taken');
  });
}

function highlightWin(line) {
  line.forEach(i => document.querySelectorAll('.cell')[i].classList.add('win'));
}

function setStatus(msg) {
  document.getElementById('status').textContent = msg;
}

function showOverlay(icon, text) {
  document.getElementById('result-icon').textContent = icon;
  document.getElementById('result-text').textContent = text;
  document.getElementById('overlay').classList.remove('hidden');
}

function updateScores() {
  document.getElementById('score-human').textContent = scores.human;
  document.getElementById('score-ai').textContent    = scores.ai;
  document.getElementById('score-draw').textContent  = scores.draw;
}

function endGame(winner) {
  gameOver = true;
  if (winner === HUMAN) {
    const line = getWinLine(board, HUMAN);
    if (line) highlightWin(line);
    scores.human++;
    updateScores();
    setTimeout(() => showOverlay('🎉', 'You Win!'), 400);
  } else if (winner === AI) {
    const line = getWinLine(board, AI);
    if (line) highlightWin(line);
    scores.ai++;
    updateScores();
    setTimeout(() => showOverlay('🤖', 'AI Wins!'), 400);
  } else {
    scores.draw++;
    updateScores();
    setTimeout(() => showOverlay('🤝', "It's a Draw!"), 400);
  }
}

function aiMove() {
  if (gameOver) return;
  setStatus('AI is thinking...');
  setTimeout(() => {
    const move = bestMove(board);
    if (move === null) return;
    board[move] = AI;
    renderBoard();
    if (checkWinner(board, AI)) { endGame(AI); return; }
    if (!availableMoves(board).length) { endGame(null); return; }
    setStatus('Your turn!');
  }, 300);
}

function handleClick(e) {
  const i = parseInt(e.target.dataset.index);
  if (gameOver || board[i] !== '') return;
  board[i] = HUMAN;
  renderBoard();
  if (checkWinner(board, HUMAN)) { endGame(HUMAN); return; }
  if (!availableMoves(board).length) { endGame(null); return; }
  aiMove();
}

function startGame() {
  board = Array(9).fill('');
  gameOver = false;
  renderBoard();
  document.getElementById('overlay').classList.add('hidden');
  if (humanFirst) {
    setStatus('Your turn!');
  } else {
    setStatus('AI goes first...');
    aiMove();
  }
}

function closeOverlay() {
  startGame();
}

function setFirst(who) {
  humanFirst = who === 'human';
  document.getElementById('btn-human').classList.toggle('active', humanFirst);
  document.getElementById('btn-ai').classList.toggle('active', !humanFirst);
  startGame();
}

document.getElementById('board').addEventListener('click', e => {
  if (e.target.classList.contains('cell')) handleClick(e);
});

document.getElementById('restart-btn').addEventListener('click', startGame);

startGame();
