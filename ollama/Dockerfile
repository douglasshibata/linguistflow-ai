FROM ollama/ollama:0.5.4

# Instala openssl e ca-certificates ignorando SSL temporariamente
RUN apt-get update -o Acquire::https::Verify-Peer=false \
    && apt-get install -y --no-install-recommends ca-certificates openssl \
    && rm -rf /var/lib/apt/lists/*

# Truque: Captura o certificado do proxy que está interceptando registry.ollama.ai 
# e o instala no sistema como uma CA confiável.
RUN openssl s_client -showcerts -connect registry.ollama.ai:443 </dev/null 2>/dev/null \
    | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' \
    > /usr/local/share/ca-certificates/corporate-proxy.crt \
    && update-ca-certificates
