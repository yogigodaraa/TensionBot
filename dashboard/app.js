const express = require('express')
const http = require('http')
const socketIo = require('socket.io')
const cors = require('cors')
const helmet = require('helmet')
const compression = require('compression')
const morgan = require('morgan')
const path = require('path')

const app = express()
const server = http.createServer(app)
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
})

const PORT = process.env.PORT || 3000
const HOST = process.env.HOST || '0.0.0.0'

// Middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.socket.io", "https://cdn.jsdelivr.net"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
      fontSrc: ["'self'", "https://cdn.jsdelivr.net"],
      connectSrc: ["'self'", "ws:", "wss:"],
      imgSrc: ["'self'", "data:", "https:"]
    }
  }
}))
app.use(compression())
app.use(morgan('combined'))
app.use(cors())
app.use(express.json({ limit: '10mb' }))
app.use(express.static(path.join(__dirname, 'public')))

// In-memory storage for recent data
const recentData = []
const MAX_STORED_RECORDS = 1000
const connectedClients = new Set()

// Store system statistics
const stats = {
  totalReceived: 0,
  startTime: new Date(),
  lastReceived: null,
  uniqueMoorings: new Set(),
  dataRate: 0
}

// Calculate data rate every minute
setInterval(() => {
  const now = new Date()
  const oneMinuteAgo = new Date(now.getTime() - 60000)
  const recentCount = recentData.filter(d => new Date(d.timestamp) > oneMinuteAgo).length
  stats.dataRate = recentCount
}, 60000).unref() // don't keep the process alive on its own (e.g. in tests)

// API Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'dashboard.html'))
})

app.get('/api/status', (req, res) => {
  const uptime = Math.floor((new Date() - stats.startTime) / 1000)
  res.json({
    status: 'running',
    uptime: uptime,
    totalReceived: stats.totalReceived,
    connectedClients: connectedClients.size,
    uniqueMoorings: stats.uniqueMoorings.size,
    dataRate: stats.dataRate,
    lastReceived: stats.lastReceived,
    memoryUsage: process.memoryUsage(),
    version: '1.0.0'
  })
})

app.get('/api/recent-data', (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 100, 500)
  const limitedData = recentData.slice(-limit)
  res.json({
    data: limitedData,
    total: recentData.length,
    returned: limitedData.length
  })
})

app.get('/api/moorings', (req, res) => {
  const moorings = {}
  recentData.forEach(record => {
    if (!moorings[record.mooring_id]) {
      moorings[record.mooring_id] = {
        mooring_id: record.mooring_id,
        location: record.location,
        lastSeen: record.timestamp,
        sensorCount: record.sensors.length,
        status: 'active'
      }
    } else {
      // Update with most recent data
      if (new Date(record.timestamp) > new Date(moorings[record.mooring_id].lastSeen)) {
        moorings[record.mooring_id].lastSeen = record.timestamp
      }
    }
  })
  
  // Mark moorings as inactive if not seen in last 5 minutes
  const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000)
  Object.values(moorings).forEach(mooring => {
    if (new Date(mooring.lastSeen) < fiveMinutesAgo) {
      mooring.status = 'inactive'
    }
  })
  
  res.json(Object.values(moorings))
})

// Endpoint to receive mooring data
app.post('/api/mooring-data', (req, res) => {
  try {
    const data = req.body
    
    // Validate basic structure
    if (!data.mooring_id || !data.timestamp || !data.sensors) {
      return res.status(400).json({
        status: 'error',
        message: 'Invalid data format: missing required fields'
      })
    }
    
    // Add reception timestamp
    data.received_at = new Date().toISOString()
    
    // Store data
    recentData.push(data)
    if (recentData.length > MAX_STORED_RECORDS) {
      recentData.shift() // Remove oldest record
    }
    
    // Update statistics
    stats.totalReceived++
    stats.lastReceived = new Date().toISOString()
    stats.uniqueMoorings.add(data.mooring_id)
    
    // Emit to connected clients
    io.emit('newMooringData', data)
    
    console.log(`📊 Received data from ${data.mooring_id} at ${data.timestamp} (${stats.totalReceived} total)`)
    
    res.json({
      status: 'success',
      message: 'Mooring data received',
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error processing mooring data:', error)
    res.status(500).json({
      status: 'error',
      message: 'Internal server error',
      details: error.message
    })
  }
})

// WebSocket handling
io.on('connection', (socket) => {
  connectedClients.add(socket.id)
  console.log(`🔌 Client connected: ${socket.id} (${connectedClients.size} total)`)
  
  // Send current stats to new client
  socket.emit('stats', {
    totalReceived: stats.totalReceived,
    uniqueMoorings: stats.uniqueMoorings.size,
    dataRate: stats.dataRate,
    lastReceived: stats.lastReceived
  })
  
  // Send recent data to new client
  const recentRecords = recentData.slice(-10) // Last 10 records
  socket.emit('recentData', recentRecords)
  
  socket.on('disconnect', () => {
    connectedClients.delete(socket.id)
    console.log(`🔌 Client disconnected: ${socket.id} (${connectedClients.size} remaining)`)
  })
  
  // Handle client requests for historical data
  socket.on('requestData', (params) => {
    const limit = Math.min(params.limit || 100, 500)
    const data = recentData.slice(-limit)
    socket.emit('historicalData', data)
  })
})

// Periodic stats broadcast
setInterval(() => {
  io.emit('stats', {
    totalReceived: stats.totalReceived,
    uniqueMoorings: stats.uniqueMoorings.size,
    dataRate: stats.dataRate,
    lastReceived: stats.lastReceived,
    connectedClients: connectedClients.size
  })
}, 5000).unref() // Every 5 seconds

// Error handling
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err)
  res.status(500).json({
    status: 'error',
    message: 'Internal server error'
  })
})

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    status: 'error',
    message: 'Endpoint not found'
  })
})

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Received SIGINT. Shutting down gracefully...')
  server.close(() => {
    console.log('👋 Server closed')
    process.exit(0)
  })
})

// Start server only when run directly (`node app.js`), not when required by tests
if (require.main === module) {
  server.listen(PORT, HOST, () => {
    console.log(`🚀 Mooring Data Dashboard running at http://${HOST}:${PORT}`)
    console.log(`📊 Ready to receive data at http://${HOST}:${PORT}/api/mooring-data`)
    console.log(`🔌 WebSocket support enabled for real-time updates`)
    console.log('\nPress Ctrl+C to stop')
  })
}

module.exports = app