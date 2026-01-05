# Este módulo foi movido para 'core/socket.mp'.
# Mantido apenas por compatibilidade e não expõe nenhuma nova definição.
"""DEPRECATED: Use core/socket.mp instead. Kept for backward compatibility."""

class TcpClient {
    """
    DEPRECATED: TCP client wrapper (use core/socket.mp instead).
    """
    static intent connect(host: string, port: int, timeout) {
        """
        Connects to TCP server.
        
        Args:
            host: Server hostname
            port: Server port
            timeout: Connection timeout
        
        Returns:
            TcpConnection instance
        """
        return TcpConnection.connect(host, port, timeout)
    }
}
