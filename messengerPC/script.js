// ДАННЫЕ
const chats = [{
  id: 'tanks',
  name: 'Танки 2024',
  avatarLetter: 'Т',
  subtitle: 'Сегодня в танки',
  badgeTime: 'сб',
  badgeCount: '34',
  members: ['Артем Аксенов', 'Артём Артемов'],
  link: 't.me/tanks2024',
  messages: [
    { text: 'Го дружить', time: '17:15', sender: 'received' },
    { text: 'Го', time: '17:15', sender: 'sent' },
    { text: 'Го Warthander скачаем', time: '18:21', sender: 'received' },
    { text: 'Го', time: '18:21', sender: 'sent' },
    { text: 'Сегодня в танчики', time: '11:47', sender: 'received' },
    { text: 'Го', time: '11:47', sender: 'sent' },
    { text: 'Сегодня в танки', time: '15:39', sender: 'sent' },
  ]
}, {
  id: 'vasya',
  name: 'Вася',
  avatarLetter: 'В',
  subtitle: 'Го сегодня на ре...',
  badgeTime: '13:35',
  badgeCount: '2',
  members: ['Вася', 'Петя'],
  link: 't.me/vasya',
  messages: [
    { text: 'Привет', time: '12:00', sender: 'received' },
    { text: 'Здарова', time: '12:01', sender: 'sent' },
  ]
}];

let currentPage = 'profile';
let currentChatId = null;
let historyStack = [];

function getChat(id) {
  return chats.find(c => c.id === id);
}

function setHeader(title, avatarLetter = null, showBack = false) {
  const headerTitle = document.getElementById('headerTitle');
  const headerAvatar = document.getElementById('headerAvatar');
  const backBtn = document.getElementById('backBtn');
  headerTitle.textContent = title;
  if (avatarLetter) {
    headerAvatar.style.display = 'flex';
    headerAvatar.textContent = avatarLetter;
  } else {
    headerAvatar.style.display = 'none';
  }
  backBtn.style.display = showBack ? 'block' : 'none';
}

function renderContent(html) {
  const content = document.getElementById('content');
  content.classList.remove('page');
  requestAnimationFrame(() => {
    content.innerHTML = html;
    content.classList.add('page');
  });
}

// НАВИГАЦИЯ
function navigateTo(page, data = null) {
  if (page !== 'back') {
    historyStack.push({ page: currentPage, chatId: currentChatId });
  }
  currentPage = page;
  if (page === 'chat' && data) {
    currentChatId = data;
  } else if (page === 'chatMenu' && data) {
    currentChatId = data;
  } else {
    currentChatId = null;
  }

  switch (page) {
    case 'profile':
      renderProfile();
      break;
    case 'communities':
      renderCommunities();
      break;
    case 'contacts':
      renderContacts();
      break;
    case 'chat':
      renderChat(currentChatId);
      break;
    case 'chatMenu':
      renderChatMenu(currentChatId);
      break;
    case 'register':
      renderRegister();
      break;
    default:
      renderProfile();
  }
}

function goBack() {
  if (historyStack.length === 0) return;
  const prev = historyStack.pop();
  if (prev.page === 'chat' || prev.page === 'chatMenu') {
    navigateTo(prev.page, prev.chatId);
  } else {
    navigateTo(prev.page);
  }
}

// РЕНДЕР СТРАНИЦ

// ---- Профиль ----
function renderProfile() {
  setHeader('Профиль', null, false);
  const html = `
    <div class="profile-top">
      <img src="https://i.yapx.ru/d3KH0.png" class="profile-avatar-lg" alt="Аватар" />
      <div>
        <div class="profile-name">Никита Корнейков</div>
        <div class="profile-phone">+7 960 553 76 58</div>
      </div>
    </div>
    <div class="profile-media">
      <div class="media-btn"><img src="https://img.icons8.com/?size=100&id=spuwtE4BmE3Q&format=png&color=1A1A1A" alt="" /> фото</div>
      <div class="media-btn"><img src="https://img.icons8.com/?size=100&id=ZI2N2LpZcXuZ&format=png&color=1A1A1A" alt="" /> видео</div>
    </div>
    <div class="post-card">
      <div class="post-header">
        <img src="https://i.yapx.ru/d3KH0.png" class="post-avatar" alt="" />
        <span class="post-author">Никита Корнейков</span>
      </div>
      <img src="https://i.yapx.ru/d3KoA.png" class="post-image" alt="Пост" />
      <div class="post-actions">
        <img src="https://img.icons8.com/?size=100&id=86721&format=png&color=1A1A1A" class="icon-action" id="likeBtn" data-liked="false" alt="Лайк" onclick="toggleLike(this)" />
        <img src="https://img.icons8.com/?size=100&id=11167&format=png&color=1A1A1A" class="icon-action" alt="Комментарий" />
        <img src="https://img.icons8.com/?size=100&id=xQweI6SpY03f&format=png&color=1A1A1A" class="icon-action" alt="Поделиться" />
      </div>
    </div>
  `;
  renderContent(html);
}

function toggleLike(el) {
  const isLiked = el.dataset.liked === 'true';
  if (!isLiked) {
    el.src = "https://img.icons8.com/?size=100&id=10287&format=png&color=1A1A1A";
    el.classList.add('liked');
    el.dataset.liked = 'true';
  } else {
    el.src = "https://img.icons8.com/?size=100&id=86721&format=png&color=1A1A1A";
    el.classList.remove('liked');
    el.dataset.liked = 'false';
  }
}

// ---- Сообщества ----
function renderCommunities() {
  setHeader('Сообщества', null, false);
  const html = `
    <div class="comm-section">
      <div class="section-title">недавно посещаемые:</div>
      <div class="comm-grid">
        <div class="comm-card">
          <img src="https://1s4oyld5dc.ucarecd.net/8fd5143c-5a69-4fc4-8297-550dc43f64e6/" alt="сообщество 1" />
          <span class="comm-name">Многопрофильный клуб</span>
        </div>
        <div class="comm-card">
          <img src="https://1s4oyld5dc.ucarecd.net/3f30d429-5ab9-4157-9d9e-753b26a7d1e9/" alt="сообщество 2" />
          <span class="comm-name">Русское географическое</span>
        </div>
      </div>
    </div>
    <div class="comm-section">
      <div class="section-title">Все сообщества:</div>
      <div class="comm-grid">
        <div class="comm-card">
          <img src="https://1s4oyld5dc.ucarecd.net/8fd5143c-5a69-4fc4-8297-550dc43f64e6/" alt="Многопрофильный клуб" />
          <span class="comm-name">Многопрофильный клуб</span>
        </div>
        <div class="comm-card">
          <img src="https://1s4oyld5dc.ucarecd.net/3f30d429-5ab9-4157-9d9e-753b26a7d1e9/" alt="Русское географическое" />
          <span class="comm-name">Русское географическое</span>
        </div>
        <div class="comm-card">
          <img src="https://1s4oyld5dc.ucarecd.net/bb50c0a6-df4c-40ab-904f-1f2081191667/" alt="Кафедра ИТ" />
          <span class="comm-name">Кафедра ИТ</span>
        </div>
        <div class="comm-card">
          <img src="https://1s4oyld5dc.ucarecd.net/da549fed-c181-4473-ad10-c359514eea9c/" alt="Кафедра ОПиПК Б..." />
          <span class="comm-name">Кафедра ОПиПК Б...</span>
        </div>
      </div>
      <hr />
      <div class="show-all">Показать все ></div>
    </div>
  `;
  renderContent(html);
}

// ---- Контакты ----
function renderContacts() {
  setHeader('История контактов', null, false);
  const contacts = [
    { name: 'Артем Аксенов', date: 'Завершённый - 27 мая' },
    { name: 'Артем Аксенов', date: 'Завершённый - 18 мая' },
    { name: 'Артем Аксенов', date: 'Завершённый - 22 апреля' },
  ];
  let html = '';
  contacts.forEach(c => {
    html += `
      <div class="contact-card">
        <div class="avatar-lg">А</div>
        <div class="contact-name">${c.name}</div>
        <div class="contact-meta">
          <img src="https://img.icons8.com/?size=100&id=99842&format=png&color=FA5252" alt="завершён" />
          <div class="date">${c.date}</div>
        </div>
      </div>
    `;
  });
  renderContent(html);
}

// ---- Чат ----
function renderChat(chatId) {
  const chat = getChat(chatId);
  if (!chat) return;
  
  setHeader(chat.name, chat.avatarLetter, false);
  document.getElementById('headerTitle').onclick = () => {
    historyStack.push({ page: 'chat', chatId: chatId });
    navigateTo('chatMenu', chatId);
  };
  document.getElementById('headerAvatar').onclick = () => {
    historyStack.push({ page: 'chat', chatId: chatId });
    navigateTo('chatMenu', chatId);
  };

  let messagesHtml = '';
  let lastDate = '';
  chat.messages.forEach(msg => {
    const date = msg.time;
    if (date !== lastDate) {
      messagesHtml += `<div class="message-date">${date}</div>`;
      lastDate = date;
    }
    messagesHtml += `
      <div class="message ${msg.sender}">
        ${msg.text}
        <span class="message-time">${msg.time}</span>
      </div>
    `;
  });

  const html = `
    <div class="chat-wrapper">
      <div class="messages-container" id="messagesContainer">
        ${messagesHtml}
      </div>
      <div class="chat-input-wrapper">
        <div class="chat-input-area">
          <img src="https://img.icons8.com/?size=100&id=bzwU1cEcaZoy&format=png&color=737373" alt="прикрепить" />
          <input type="text" placeholder="Сообщение" id="messageInput" />
          <img src="https://img.icons8.com/?size=100&id=61895&format=png&color=737373" alt="смайл" />
          <img src="https://img.icons8.com/?size=100&id=59836&format=png&color=737373" alt="голос" />
          <img src="https://img.icons8.com/?size=100&id=100004&format=png&color=737373" alt="отправить" onclick="sendMessage()" />
        </div>
      </div>
    </div>
  `;
  
  renderContent(html);
  
  setTimeout(() => {
    const container = document.getElementById('messagesContainer');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, 100);
}

// ---- Отправка сообщения ----
function sendMessage() {
  const input = document.getElementById('messageInput');
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;

  const chat = getChat(currentChatId);
  if (!chat) return;

  const now = new Date();
  const time = now.getHours().toString().padStart(2, '0') + ':' + 
               now.getMinutes().toString().padStart(2, '0');
  
  chat.messages.push({
    text: text,
    time: time,
    sender: 'sent'
  });

  input.value = '';
  renderChat(currentChatId);
}

// ---- Отправка по Enter ----
document.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && document.getElementById('messageInput')) {
    const input = document.getElementById('messageInput');
    if (document.activeElement === input) {
      e.preventDefault();
      sendMessage();
    }
  }
});

// ---- Меню чата ----
function renderChatMenu(chatId) {
  const chat = getChat(chatId);
  if (!chat) return;
  setHeader(chat.name, chat.avatarLetter, true);
  document.getElementById('backBtn').onclick = () => {
    goBack();
  };

  let membersHtml = '';
  chat.members.forEach(m => {
    membersHtml += `
      <div class="member-row">
        <div class="member-avatar">${m.charAt(0)}</div>
        <div class="member-name">${m}</div>
      </div>
    `;
  });

  const html = `
    <div class="chat-menu-wrapper">
      <div class="chat-menu-profile">
        <div class="chat-menu-avatar">${chat.avatarLetter}</div>
        <div class="chat-menu-name">${chat.name}</div>
      </div>
      <div class="menu-actions">
        <div class="menu-action-btn" onclick="navigateTo('contacts')">
          <img src="https://img.icons8.com/?size=100&id=78382&format=png&color=1A1A1A" alt="контакты" />
          контакты
        </div>
        <div class="menu-action-btn" onclick="alert('Уведомления')">
          <img src="https://img.icons8.com/?size=100&id=83158&format=png&color=1A1A1A" alt="уведомления" />
          уведомления
        </div>
        <div class="menu-action-btn" onclick="alert('Ещё')">
          <img src="https://img.icons8.com/?size=100&id=21622&format=png&color=1A1A1A" alt="ещё" />
          ещё
        </div>
      </div>
      <div class="chat-menu-section">Ссылка на чат</div>
      <div class="menu-link-row">${chat.link}</div>
      <div class="chat-menu-section">Участники</div>
      ${membersHtml}
    </div>
  `;
  renderContent(html);
}

// ---- Регистрация (внутри приложения) ----
function renderRegister() {
  setHeader('Регистрация', null, false);
  const html = `
    <div class="register-card" style="max-width:500px; margin:30px auto;">
      <img src="https://img.icons8.com/?size=100&id=oQZiODxTvE5b&format=png&color=000000" class="logo" alt="VEX" />
      <div class="title">Регистрация</div>
      <form id="registerFormInner" onsubmit="registerSubmitInner(event)">
        <input type="text" placeholder="Введите имя пользователя" required />
        <input type="text" placeholder="Ф.И.О." required />
        <input type="email" placeholder="email (не обяз.)" />
        <input type="tel" placeholder="Введите номер телефона" required />
        <div class="agree">
          <input type="checkbox" id="agreeCheckInner" required />
          <label for="agreeCheckInner">вы соглашаетесь с <a href="#">политикой конфиденциальности</a></label>
        </div>
        <button type="submit" class="btn-register">Зарегистрироваться</button>
      </form>
    </div>
  `;
  renderContent(html);
}

function registerSubmitInner(e) {
  e.preventDefault();
  alert('Вы зарегистрированы! Переход в профиль.');
  navigateTo('profile');
}

// СПИСОК ЧАТОВ + ПОИСК
function renderChatList() {
  const container = document.getElementById('chatList');
  container.innerHTML = '';
  chats.forEach(chat => {
    const item = document.createElement('div');
    item.className = 'chat-item';
    item.innerHTML = `
      <div class="avatar">${chat.avatarLetter}</div>
      <div class="chat-content">
        <div class="chat-title">${chat.name}</div>
        <div class="chat-subtitle">${chat.subtitle}</div>
      </div>
      <div class="chat-badges">
        <div class="badge">${chat.badgeTime}</div>
        <div class="badge">${chat.badgeCount}</div>
      </div>
    `;
    item.addEventListener('click', () => {
      historyStack = [];
      navigateTo('chat', chat.id);
    });
    container.appendChild(item);
  });
}

document.getElementById('searchInput').addEventListener('input', function(e) {
  const query = e.target.value.toLowerCase();
  const items = document.querySelectorAll('.chat-item');
  items.forEach(item => {
    const title = item.querySelector('.chat-title').textContent.toLowerCase();
    item.style.display = title.includes(query) ? 'flex' : 'none';
  });
});

// ОБРАБОТЧИК ПОЛНОЭКРАННОЙ РЕГИСТРАЦИИ
document.getElementById('registerForm').addEventListener('submit', function(e) {
  e.preventDefault();
  document.getElementById('register-overlay').classList.add('hidden');
  document.getElementById('app').classList.add('active');
  renderChatList();
  navigateTo('profile');
});