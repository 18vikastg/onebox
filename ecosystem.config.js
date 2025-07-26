module.exports = {
  apps: [
    {
      name: 'reachinbox-web',
      script: 'index.js',
      instances: 1,
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        PORT: 4000
      },
      error_file: './logs/web-error.log',
      out_file: './logs/web-out.log',
      log_file: './logs/web-combined.log',
      time: true,
      max_memory_restart: '500M',
      restart_delay: 4000,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'reachinbox-email-sync',
      script: 'email_sync_service.py',
      interpreter: 'python3',
      instances: 1,
      env: {
        PYTHONPATH: '.',
        NODE_ENV: 'production'
      },
      error_file: './logs/sync-error.log',
      out_file: './logs/sync-out.log',
      log_file: './logs/sync-combined.log',
      time: true,
      max_memory_restart: '300M',
      restart_delay: 4000,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false,
      ignore_watch: ['node_modules', 'logs', '*.log']
    }
  ]
};
