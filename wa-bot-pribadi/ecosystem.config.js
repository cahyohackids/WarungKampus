// ============================================
//  PM2 ECOSYSTEM CONFIG
//  Jalankan: pm2 start ecosystem.config.js
// ============================================

module.exports = {
    apps: [{
        name: 'wa-bot-pribadi',
        script: 'index.js',
        watch: false,
        autorestart: true,
        restart_delay: 5000,
        max_restarts: 10,
        max_memory_restart: '500M',
        env: {
            NODE_ENV: 'production',
        },
        // Log files
        error_file: './logs/error.log',
        out_file: './logs/output.log',
        log_date_format: 'YYYY-MM-DD HH:mm:ss',
        // Merge stdout and stderr
        merge_logs: true,
    }],
};
