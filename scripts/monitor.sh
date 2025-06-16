echo "📊 App Reviewer Status"
echo "======================"

docker-compose ps

echo ""
echo "📋 Recent Logs (Backend):"
docker-compose logs --tail=20 backend

echo ""
echo "📋 Recent Logs (Frontend):"
docker-compose logs --tail=20 frontend