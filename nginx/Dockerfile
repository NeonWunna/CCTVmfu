FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 8010
EXPOSE 8020

CMD ["nginx", "-g", "daemon off;"]
