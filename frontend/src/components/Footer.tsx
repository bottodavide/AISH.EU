export function Footer() {
  return (
    <footer className="bg-gray-900 text-white mt-auto">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p>&copy; {new Date().getFullYear()} AI Strategy Hub. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
