(async function () {
  const response = await fetch("data/members.json");
  if (!response.ok) {
    console.error("Failed to load members.json", response.status);
    return;
  }

  const members = await response.json();
  console.log("Member count:", members.length);
})();
