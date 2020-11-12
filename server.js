const path = require('path');
const http = require('http');
const express = require('express');
const socketio = require('socket.io');
const formatMessage = require('./utils/messages');

let accounts = [
  {
    "id": 1,
    "username": "paulhal",
    "password": "admin",
    "channel" : "1234",
  }
];

const {
  userJoin,
  getCurrentUser,
  userLeave,
  getRoomUsers
} = require('./utils/users');

const app = express();
const server = http.createServer(app);
const io = socketio(server);

// Set static folder
app.use(express.static(path.join(__dirname, 'public')));


// Run when client connects
io.on('connection', socket => {
  socket.on('joinRoom', ({ username, room }) => {
    const user = userJoin(socket.id, username, room);
    socket.join(user.room);
    // Send users and room info
    io.to(user.room).emit('roomUsers', {
      room: user.room,
      users: getRoomUsers(user.room)
    });
  });

  //send audio message
  socket.on("audioMessage", function(msg) {
    const user = getCurrentUser(socket.id);
    //socket.broadcast.emit("audioMessage", msg);
    socket.broadcast.to(user.room).emit("audioMessage", msg);
  });


  // Listen for chatMessage
  socket.on('chatMessage', msg => {
    const user = getCurrentUser(socket.id);
    io.to(user.room).emit('message', formatMessage(user.username, msg));
  });

  // Runs when client disconnects
  socket.on('disconnect', () => {
    const user = userLeave(socket.id);
      // Send users and room info
      io.to(user.room).emit('roomUsers', {
        room: user.room,
        users: getRoomUsers(user.room)
      })
    });
});

app.get('/ptt', function (req, res) {
  res.sendFile(path.join(__dirname, 'public/ptt.html'));
});

app.get('/manage', function (req, res) {
  res.sendFile(path.join(__dirname, 'public/manage.html'));
});

const PORT = process.env.PORT || 9999;

server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
