const Footer = () => {
  return (
    <div>
      <footer className="text-white text-sm text-center absolute bottom-0 w-full left-0">
        <p>
          © 2025 NcDashboard - Build version{" "}
          <a
            target="_blank"
            rel="noopener noreferrer"
            className="underline"
            href={`https://github.com/olmozavala/ncdashboard/commit/${process.env.VITE_COMMIT_HASH}`}
          >
            {process.env.VITE_COMMIT_HASH}
          </a>
        </p>
      </footer>
    </div>
  );
};

export default Footer;
