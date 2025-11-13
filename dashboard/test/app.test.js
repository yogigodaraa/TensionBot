const request = require('supertest')
const app = require('./app')

describe('Mooring Data Dashboard API', () => {
  describe('GET /', () => {
    it('should return the dashboard HTML', async () => {
      const response = await request(app)
        .get('/')
        .expect(200)
      
      expect(response.headers['content-type']).toMatch(/text\/html/)
    })
  })

  describe('GET /api/status', () => {
    it('should return system status', async () => {
      const response = await request(app)
        .get('/api/status')
        .expect(200)
      
      expect(response.body).toHaveProperty('status', 'running')
      expect(response.body).toHaveProperty('uptime')
      expect(response.body).toHaveProperty('totalReceived')
      expect(response.body).toHaveProperty('connectedClients')
    })
  })

  describe('POST /api/mooring-data', () => {
    it('should accept valid mooring data', async () => {
      const validData = {
        mooring_id: 'MOOR_TEST',
        timestamp: new Date().toISOString(),
        location: { latitude: -20.7256, longitude: 116.8456 },
        sensors: [{
          sensor_id: 'MOOR_TEST_SENSOR_01',
          sensor_type: 'temperature',
          value: 23.5,
          unit: '°C',
          timestamp: new Date().toISOString(),
          quality: 'good'
        }],
        weather: {
          conditions: 'clear',
          visibility: 15.0,
          humidity: 75.0,
          sea_state: 2,
          swell_height: 1.5,
          swell_period: 8.0
        },
        system_status: {
          battery_level: 85.5,
          signal_strength: -70,
          data_transmission_rate: 98.2,
          last_maintenance: '2024-10-15T10:30:00Z',
          operational_days: 45,
          alerts: []
        }
      }

      const response = await request(app)
        .post('/api/mooring-data')
        .send(validData)
        .expect(200)
      
      expect(response.body).toHaveProperty('status', 'success')
      expect(response.body).toHaveProperty('message', 'Mooring data received')
    })

    it('should reject invalid data format', async () => {
      const invalidData = {
        invalid: 'data'
      }

      const response = await request(app)
        .post('/api/mooring-data')
        .send(invalidData)
        .expect(400)
      
      expect(response.body).toHaveProperty('status', 'error')
    })
  })

  describe('GET /api/recent-data', () => {
    it('should return recent data array', async () => {
      const response = await request(app)
        .get('/api/recent-data')
        .expect(200)
      
      expect(response.body).toHaveProperty('data')
      expect(response.body).toHaveProperty('total')
      expect(response.body).toHaveProperty('returned')
      expect(Array.isArray(response.body.data)).toBe(true)
    })
  })

  describe('GET /api/moorings', () => {
    it('should return moorings array', async () => {
      const response = await request(app)
        .get('/api/moorings')
        .expect(200)
      
      expect(Array.isArray(response.body)).toBe(true)
    })
  })
})