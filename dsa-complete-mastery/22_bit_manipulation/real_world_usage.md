# Bit Manipulation — Real-World Usage

Bit manipulation is the language of hardware. Unix permissions, feature flags,
IPv4 networking, probabilistic data structures, graphics pipelines, and
cryptographic primitives all encode information in individual bits and use
bitwise operations for speed and compactness. Every example below is taken
directly from production systems.

---

## 1. Permission Systems — Unix File Permissions

### The Production Problem

Every file on a Unix/Linux/macOS system has a 12-bit permission field. The
visible 9 bits encode three groups (owner, group, other) × three permissions
(read, write, execute). When you run `chmod 755 deploy.sh`, the kernel stores
0b111101101 in the inode. Every `ls -l`, every `open()` syscall, every file
access check uses bitwise AND against this field. The kernel does millions of
these per second — they must be single-instruction operations.

```python
# -----------------------------------------------------------------------
# Unix file permission system — exact model of the kernel's inode bitmask
# -----------------------------------------------------------------------

class FilePermissions:
    """
    Models Unix file permissions as a 9-bit integer (3 groups × 3 perms).
    This is the exact representation stored in struct stat's st_mode field.

    Bits:
      8-6: owner (rwx)
      5-3: group (rwx)
      2-0: other (rwx)
    """

    # Permission bit masks — identical to constants in sys/stat.h
    OWNER_READ    = 0o400   # 0b100000000
    OWNER_WRITE   = 0o200   # 0b010000000
    OWNER_EXECUTE = 0o100   # 0b001000000
    GROUP_READ    = 0o040   # 0b000100000
    GROUP_WRITE   = 0o020   # 0b000010000
    GROUP_EXECUTE = 0o010   # 0b000001000
    OTHER_READ    = 0o004   # 0b000000100
    OTHER_WRITE   = 0o002   # 0b000000010
    OTHER_EXECUTE = 0o001   # 0b000000001

    # Named permission sets used in chmod
    PERMISSION_NAMES = {
        "owner_read"    : OWNER_READ,
        "owner_write"   : OWNER_WRITE,
        "owner_execute" : OWNER_EXECUTE,
        "group_read"    : GROUP_READ,
        "group_write"   : GROUP_WRITE,
        "group_execute" : GROUP_EXECUTE,
        "other_read"    : OTHER_READ,
        "other_write"   : OTHER_WRITE,
        "other_execute" : OTHER_EXECUTE,
    }

    def __init__(self, mode: int = 0o000):
        """
        Initialize with an octal permission value.
        e.g., FilePermissions(0o755) mirrors `chmod 755 file`
        """
        self._mode = mode & 0o777  # mask to 9 bits

    # ------------------------------------------------------------------
    # Query operations — bitwise AND
    # ------------------------------------------------------------------

    def has_permission(self, bit: int) -> bool:
        """Test a single permission bit using AND. O(1) — single instruction."""
        return bool(self._mode & bit)

    def has_read(self, who: str = "owner") -> bool:
        bit = {"owner": self.OWNER_READ, "group": self.GROUP_READ, "other": self.OTHER_READ}[who]
        return self.has_permission(bit)

    def has_write(self, who: str = "owner") -> bool:
        bit = {"owner": self.OWNER_WRITE, "group": self.GROUP_WRITE, "other": self.OTHER_WRITE}[who]
        return self.has_permission(bit)

    def has_execute(self, who: str = "owner") -> bool:
        bit = {"owner": self.OWNER_EXECUTE, "group": self.GROUP_EXECUTE, "other": self.OTHER_EXECUTE}[who]
        return self.has_permission(bit)

    def can_access(self, who: str, operation: str) -> bool:
        """Generic permission check. Used by the kernel's permission() function."""
        op_map = {"read": self.has_read, "write": self.has_write, "execute": self.has_execute}
        return op_map[operation](who)

    # ------------------------------------------------------------------
    # Modification operations — bitwise OR and AND NOT
    # ------------------------------------------------------------------

    def add_permission(self, bit: int) -> "FilePermissions":
        """Grant a permission: set the bit using OR. Like: chmod u+x file"""
        self._mode |= bit
        return self

    def remove_permission(self, bit: int) -> "FilePermissions":
        """Revoke a permission: clear the bit using AND NOT. Like: chmod o-w file"""
        self._mode &= ~bit
        return self

    def set_mode(self, octal: int) -> "FilePermissions":
        """Replace all permissions at once. Like: chmod 644 file"""
        self._mode = octal & 0o777
        return self

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def to_octal(self) -> str:
        return oct(self._mode)

    def to_rwx_string(self) -> str:
        """Produce the 'rwxrwxrwx' string shown by `ls -l`."""
        chars = ""
        for bit in [
            self.OWNER_READ, self.OWNER_WRITE, self.OWNER_EXECUTE,
            self.GROUP_READ, self.GROUP_WRITE, self.GROUP_EXECUTE,
            self.OTHER_READ, self.OTHER_WRITE, self.OTHER_EXECUTE,
        ]:
            chars += "rwx"[([self.OWNER_READ, self.OWNER_WRITE, self.OWNER_EXECUTE,
                              self.GROUP_READ, self.GROUP_WRITE, self.GROUP_EXECUTE,
                              self.OTHER_READ, self.OTHER_WRITE, self.OTHER_EXECUTE].index(bit)) % 3] \
                     if self._mode & bit else "-"
        return chars

    def __repr__(self):
        return f"FilePermissions({self.to_octal()} = {self.to_rwx_string()})"


# -----------------------------------------------------------------------
# Demo: common chmod scenarios
# -----------------------------------------------------------------------

scenarios = [
    (0o755, "deploy.sh",    "Executable script (owner: rwx, group+other: r-x)"),
    (0o644, "config.yaml",  "Config file (owner: rw-, group+other: r--)"),
    (0o600, "private.key",  "Private key (owner: rw-, group+other: ---)"),
    (0o777, "public.txt",   "World-writable (owner+group+other: rwx) — bad practice"),
    (0o400, "readonly.conf","Read-only (owner: r--, group+other: ---)"),
]

print(f"{'File':<20} {'Octal':>6}  {'Permissions':>12}  Description")
print("-" * 80)
for mode, filename, desc in scenarios:
    p = FilePermissions(mode)
    print(f"{filename:<20} {p.to_octal():>6}  {p.to_rwx_string():>12}  {desc}")

print()

# Simulate chmod 755 from scratch using bit operations
p = FilePermissions(0o000)
p.add_permission(FilePermissions.OWNER_READ | FilePermissions.OWNER_WRITE | FilePermissions.OWNER_EXECUTE)
p.add_permission(FilePermissions.GROUP_READ | FilePermissions.GROUP_EXECUTE)
p.add_permission(FilePermissions.OTHER_READ | FilePermissions.OTHER_EXECUTE)
print(f"Built chmod 755 from scratch: {p}")
print(f"  Owner can execute: {p.has_execute('owner')}")
print(f"  Other can write:   {p.has_write('other')}")

# Simulate the kernel's permission check
private_key = FilePermissions(0o600)
print(f"\nprivate.key {private_key}")
for who in ["owner", "group", "other"]:
    for op in ["read", "write", "execute"]:
        result = private_key.can_access(who, op)
        print(f"  {who:6s} {op:8s}: {'ALLOWED' if result else 'DENIED '}")
```

---

## 2. Feature Flags — 32 Toggles in a Single Integer

### The Production Problem

Facebook's Gatekeeper, LinkedIn's supergroup flags, and LaunchDarkly all store
user feature eligibility as bitmasks. A single 32-bit integer can represent
the enabled/disabled state of 32 independent features. Storing this as a
bitmask means one database column, one cache key, one network byte instead of
32 boolean columns. Checking "is feature X enabled?" is a single CPU instruction.
This is how A/B testing infrastructure serves billions of users efficiently.

```python
from enum import IntEnum

# -----------------------------------------------------------------------
# Feature flag system using a 32-bit integer bitmask
# -----------------------------------------------------------------------

class Feature(IntEnum):
    """
    Feature flag definitions — each value is a bit position (0-31).
    New features are added by assigning the next available bit.
    Maximum: 32 features per integer (use int64 for 64, or multiple ints).
    """
    DARK_MODE          = 0
    NEW_DASHBOARD      = 1
    BETA_AI_ASSISTANT  = 2
    FASTER_CHECKOUT    = 3
    REAL_TIME_COLLAB   = 4
    EXPERIMENTAL_FEED  = 5
    PREMIUM_ANALYTICS  = 6
    ADVANCED_SEARCH    = 7
    BULK_EXPORT        = 8
    TWO_FACTOR_AUTH    = 9
    OFFLINE_MODE       = 10
    CUSTOM_THEMES      = 11
    API_V2             = 12
    CANARY_DEPLOYMENT  = 13
    NEW_NOTIFICATIONS  = 14
    PROFILE_V2         = 15


class FeatureFlags:
    """
    Bit-packed feature flag store for a single user or user segment.

    Each bit in a 32-bit integer represents one feature.
    Bit n = 1 means Feature n is ENABLED for this user.
    Bit n = 0 means Feature n is DISABLED.

    This is how production systems like Facebook's Gatekeeper work:
    one integer per user, stored in a key-value store (Redis, memcached).
    Reading a user's flags is a single O(1) cache lookup.
    Checking a flag is a single O(1) AND + compare operation.
    """

    def __init__(self, initial_flags: int = 0):
        self._flags = initial_flags  # 32-bit integer

    def enable(self, feature: Feature) -> "FeatureFlags":
        """Set the bit for this feature using OR. O(1)."""
        self._flags |= (1 << feature)
        return self

    def disable(self, feature: Feature) -> "FeatureFlags":
        """Clear the bit for this feature using AND NOT. O(1)."""
        self._flags &= ~(1 << feature)
        return self

    def toggle(self, feature: Feature) -> "FeatureFlags":
        """Flip the bit using XOR. O(1). Useful for admin toggles."""
        self._flags ^= (1 << feature)
        return self

    def is_enabled(self, feature: Feature) -> bool:
        """Test the bit using AND. O(1) — this is the hot path."""
        return bool(self._flags & (1 << feature))

    def enable_multiple(self, *features: Feature) -> "FeatureFlags":
        """Enable multiple features at once by ORing all their bits."""
        for f in features:
            self._flags |= (1 << f)
        return self

    def disable_multiple(self, *features: Feature) -> "FeatureFlags":
        for f in features:
            self._flags &= ~(1 << f)
        return self

    def enabled_features(self) -> list[Feature]:
        """Return list of all enabled features by scanning bits."""
        return [f for f in Feature if self.is_enabled(f)]

    def to_int(self) -> int:
        """Serialize to integer — store this one value in the database."""
        return self._flags

    def __repr__(self):
        enabled = [f.name for f in self.enabled_features()]
        return f"FeatureFlags(0x{self._flags:08x} = {enabled})"


# -----------------------------------------------------------------------
# Demo: user segmentation and A/B testing rollout
# -----------------------------------------------------------------------

# Define user tiers
BETA_USER_FLAGS = (
    FeatureFlags()
    .enable_multiple(
        Feature.DARK_MODE, Feature.NEW_DASHBOARD,
        Feature.BETA_AI_ASSISTANT, Feature.FASTER_CHECKOUT,
        Feature.REAL_TIME_COLLAB, Feature.EXPERIMENTAL_FEED,
        Feature.PREMIUM_ANALYTICS, Feature.ADVANCED_SEARCH,
        Feature.API_V2, Feature.NEW_NOTIFICATIONS,
    )
)

STANDARD_USER_FLAGS = (
    FeatureFlags()
    .enable_multiple(
        Feature.DARK_MODE, Feature.FASTER_CHECKOUT,
        Feature.TWO_FACTOR_AUTH, Feature.CUSTOM_THEMES,
    )
)

FREE_USER_FLAGS = FeatureFlags().enable(Feature.DARK_MODE)

print("User tier feature flags:")
print(f"  Beta user    : {BETA_USER_FLAGS}")
print(f"  Standard user: {STANDARD_USER_FLAGS}")
print(f"  Free user    : {FREE_USER_FLAGS}")
print()

# Serialized form — this is what you store in the DB
print("Serialized as single integer (stored in users table):")
print(f"  Beta     : flags_int = {BETA_USER_FLAGS.to_int()}")
print(f"  Standard : flags_int = {STANDARD_USER_FLAGS.to_int()}")
print(f"  Free     : flags_int = {FREE_USER_FLAGS.to_int()}")
print()

# Hot path: check if a feature is enabled for a user
user_flags = STANDARD_USER_FLAGS
feature_to_check = Feature.BETA_AI_ASSISTANT
print(f"Is AI Assistant enabled for standard user? "
      f"{user_flags.is_enabled(feature_to_check)}")
print(f"Is Dark Mode enabled for standard user?    "
      f"{user_flags.is_enabled(Feature.DARK_MODE)}")

# Rollout: enable API_V2 for all standard users in one bulk update
print(f"\nRolling out API_V2 to standard users...")
print(f"  Before: API_V2 = {user_flags.is_enabled(Feature.API_V2)}")
user_flags.enable(Feature.API_V2)
print(f"  After : API_V2 = {user_flags.is_enabled(Feature.API_V2)}")

# Demonstrate bitmask operations on flag integers (bulk updates)
print(f"\nEnabled features for standard user: {user_flags.enabled_features()}")
```

---

## 3. Network Masks — IPv4 Subnet Calculations

### The Production Problem

Every network engineer, cloud infrastructure engineer (AWS VPC, GCP subnets,
Azure VNets), and firewall rule author works with CIDR notation like
`10.0.0.0/16`. Determining whether two IPs are in the same subnet, calculating
the broadcast address, and checking firewall rules all reduce to bitwise AND
with a subnet mask. Linux's `ip route`, AWS security groups, and iptables all
perform these operations in the kernel's network stack millions of times per second.

```python
import struct
import socket

# -----------------------------------------------------------------------
# IPv4 subnet mask operations — pure bitwise arithmetic
# -----------------------------------------------------------------------

def ip_to_int(ip: str) -> int:
    """Convert dotted-decimal IP to 32-bit integer."""
    parts = ip.split(".")
    result = 0
    for part in parts:
        result = (result << 8) | int(part)
    return result


def int_to_ip(n: int) -> str:
    """Convert 32-bit integer back to dotted-decimal IP."""
    return ".".join([
        str((n >> 24) & 0xFF),
        str((n >> 16) & 0xFF),
        str((n >>  8) & 0xFF),
        str(n         & 0xFF),
    ])


def prefix_to_mask(prefix_len: int) -> int:
    """
    Convert prefix length to subnet mask integer.
    /24 -> 0xFFFFFF00 (255.255.255.0)
    /16 -> 0xFFFF0000 (255.255.0.0)

    Trick: all-ones 32-bit integer left-shifted by (32 - prefix_len).
    """
    if prefix_len == 0:
        return 0
    return (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF


def get_network_address(ip: str, prefix_len: int) -> str:
    """
    Network address = IP AND mask.
    The host portion of bits is zeroed out.
    This is what `ip route` shows as the network prefix.
    """
    ip_int   = ip_to_int(ip)
    mask     = prefix_to_mask(prefix_len)
    network  = ip_int & mask          # zero out host bits
    return int_to_ip(network)


def get_broadcast_address(ip: str, prefix_len: int) -> str:
    """
    Broadcast address = Network address OR (NOT mask).
    The host portion of bits is all set to 1.
    """
    ip_int    = ip_to_int(ip)
    mask      = prefix_to_mask(prefix_len)
    network   = ip_int & mask
    host_mask = ~mask & 0xFFFFFFFF    # invert: now host bits are all 1s
    broadcast = network | host_mask   # OR sets all host bits
    return int_to_ip(broadcast)


def is_in_subnet(ip: str, subnet_cidr: str) -> bool:
    """
    Check if `ip` belongs to the subnet defined by `subnet_cidr`.
    Equivalent to the check performed by iptables, AWS Security Groups,
    and Linux kernel's fib_validate_source().

    The IP is in the subnet iff:
        (ip AND mask) == (network_address AND mask)
    i.e., they share the same network portion of the address.
    """
    network_ip, prefix_str = subnet_cidr.split("/")
    prefix_len = int(prefix_str)
    mask       = prefix_to_mask(prefix_len)

    ip_net      = ip_to_int(ip)      & mask
    subnet_net  = ip_to_int(network_ip) & mask

    return ip_net == subnet_net


def get_subnet_info(cidr: str) -> dict:
    """Full subnet analysis — like `ipcalc` command."""
    network_ip, prefix_str = cidr.split("/")
    prefix_len = int(prefix_str)
    mask       = prefix_to_mask(prefix_len)

    network    = get_network_address(network_ip, prefix_len)
    broadcast  = get_broadcast_address(network_ip, prefix_len)

    # First usable = network + 1, last usable = broadcast - 1
    first_host = int_to_ip(ip_to_int(network) + 1)
    last_host  = int_to_ip(ip_to_int(broadcast) - 1)
    num_hosts  = max(0, (1 << (32 - prefix_len)) - 2)  # subtract network + broadcast

    return {
        "cidr"           : cidr,
        "network_address": network,
        "subnet_mask"    : int_to_ip(mask),
        "broadcast"      : broadcast,
        "first_host"     : first_host,
        "last_host"      : last_host,
        "usable_hosts"   : num_hosts,
        "prefix_length"  : prefix_len,
    }


# -----------------------------------------------------------------------
# Demo: AWS VPC-style subnet validation
# -----------------------------------------------------------------------

print("Subnet information (ipcalc equivalent):")
for cidr in ["10.0.0.0/8", "192.168.1.0/24", "172.16.0.0/12", "10.10.50.0/27"]:
    info = get_subnet_info(cidr)
    print(f"\n  {info['cidr']}")
    print(f"    Network   : {info['network_address']}")
    print(f"    Mask      : {info['subnet_mask']}")
    print(f"    Broadcast : {info['broadcast']}")
    print(f"    Host range: {info['first_host']} - {info['last_host']}")
    print(f"    Usable IPs: {info['usable_hosts']:,}")

print("\nSubnet membership checks (like AWS Security Group rules):")
test_cases = [
    ("10.0.5.50",      "10.0.0.0/8",    True),
    ("10.0.5.50",      "192.168.0.0/16",False),
    ("192.168.1.100",  "192.168.1.0/24",True),
    ("192.168.2.1",    "192.168.1.0/24",False),
    ("172.16.200.1",   "172.16.0.0/12", True),
]
for ip, subnet, expected in test_cases:
    result = is_in_subnet(ip, subnet)
    status = "PASS" if result == expected else "FAIL"
    print(f"  [{status}] {ip:<16} in {subnet:<20} -> {result}")
```

---

## 4. Bloom Filter Implementation — Probabilistic Membership Testing

### The Production Problem

Bloom filters are used in databases (Apache Cassandra, HBase, RocksDB,
PostgreSQL with pg_bloom), web browsers (Chrome's Safe Browsing), CDNs
(Akamai), and caches to answer "is this item definitely NOT in the set?" with
zero false negatives and a tunable false positive rate, using only a fraction
of the memory that a hash set would require. The entire data structure is a
byte array manipulated with bitwise operations.

```python
import hashlib
import math
from typing import Any

# -----------------------------------------------------------------------
# Bloom filter backed by a bytearray with bitwise operations
# -----------------------------------------------------------------------

class BloomFilter:
    """
    Classic Bloom filter using k hash functions and an m-bit array.

    Used in production by:
      - Apache Cassandra: avoid disk lookups for missing keys
      - Google Chrome: Safe Browsing malicious URL list (~1M URLs in ~8MB)
      - PostgreSQL: accelerate index scan for rare values
      - Bitcoin: SPV wallet bloom filters

    False positives are possible (returns "might contain" for absent items).
    False negatives are IMPOSSIBLE (if item was added, it will always be found).

    Space efficiency: can represent 1M items with 1% FPR in ~1.14 MB
                      vs a set which would need ~8-16 MB.
    """

    def __init__(self, capacity: int, false_positive_rate: float = 0.01):
        """
        capacity          : Expected number of items to insert.
        false_positive_rate: Desired probability of false positives (0 to 1).
        """
        self.capacity            = capacity
        self.false_positive_rate = false_positive_rate

        # Optimal bit array size: m = -(n * ln(p)) / (ln 2)^2
        self._num_bits = math.ceil(
            -(capacity * math.log(false_positive_rate)) / (math.log(2) ** 2)
        )

        # Optimal number of hash functions: k = (m/n) * ln(2)
        self._num_hashes = max(1, math.ceil(
            (self._num_bits / capacity) * math.log(2)
        ))

        # Bit array stored as a bytearray (1 byte = 8 bits)
        self._byte_array = bytearray(math.ceil(self._num_bits / 8))
        self._count = 0  # approximate count of inserted items

    def _get_bit_positions(self, item: Any) -> list[int]:
        """
        Generate k independent hash positions for an item.
        Uses double hashing: position_i = (h1 + i * h2) % m
        This is the Kirsch-Mitzenmacher technique — avoids needing k
        truly independent hash functions.
        """
        item_bytes = str(item).encode("utf-8")

        h1 = int(hashlib.md5(item_bytes).hexdigest(), 16)
        h2 = int(hashlib.sha1(item_bytes).hexdigest(), 16)

        return [(h1 + i * h2) % self._num_bits for i in range(self._num_hashes)]

    def _set_bit(self, position: int) -> None:
        """Set bit at position using OR. O(1)."""
        byte_index = position // 8
        bit_offset = position % 8
        self._byte_array[byte_index] |= (1 << bit_offset)

    def _check_bit(self, position: int) -> bool:
        """Check bit at position using AND. O(1)."""
        byte_index = position // 8
        bit_offset = position % 8
        return bool(self._byte_array[byte_index] & (1 << bit_offset))

    def add(self, item: Any) -> None:
        """
        Add an item to the filter by setting all k bit positions.
        After this, might_contain(item) is guaranteed to return True.
        """
        for pos in self._get_bit_positions(item):
            self._set_bit(pos)
        self._count += 1

    def might_contain(self, item: Any) -> bool:
        """
        Check if item MIGHT be in the filter.
        Returns True: item was probably added (or false positive).
        Returns False: item was DEFINITELY NOT added (100% certain).

        This is the hot path — called millions of times per second in
        Cassandra to avoid SSTtable disk reads for missing keys.
        """
        return all(self._check_bit(pos) for pos in self._get_bit_positions(item))

    def get_stats(self) -> dict:
        filled_bits = sum(bin(b).count("1") for b in self._byte_array)
        estimated_fpr = (filled_bits / self._num_bits) ** self._num_hashes
        return {
            "capacity"          : self.capacity,
            "items_inserted"    : self._count,
            "bit_array_size"    : self._num_bits,
            "bytes_used"        : len(self._byte_array),
            "num_hash_functions": self._num_hashes,
            "bits_set"          : filled_bits,
            "fill_ratio"        : round(filled_bits / self._num_bits, 4),
            "estimated_fpr"     : round(estimated_fpr, 6),
            "target_fpr"        : self.false_positive_rate,
        }


# -----------------------------------------------------------------------
# Demo: URL blacklist like Chrome Safe Browsing
# -----------------------------------------------------------------------

import random
import string

def random_url(length: int = 20) -> str:
    chars = string.ascii_lowercase + string.digits
    domain = "".join(random.choices(chars, k=length))
    return f"https://{domain}.com/path"

random.seed(42)

# Build a filter for 10,000 known malicious URLs with 1% FPR target
print("Chrome Safe Browsing — malicious URL filter")
print("=" * 50)

MALICIOUS_COUNT = 10_000
FPR_TARGET = 0.01

bloom = BloomFilter(capacity=MALICIOUS_COUNT, false_positive_rate=FPR_TARGET)

malicious_urls = [random_url(15) for _ in range(MALICIOUS_COUNT)]
for url in malicious_urls:
    bloom.add(url)

stats = bloom.get_stats()
print(f"Items inserted    : {stats['items_inserted']:,}")
print(f"Bit array size    : {stats['bit_array_size']:,} bits ({stats['bytes_used']:,} bytes = {stats['bytes_used']/1024:.1f} KB)")
print(f"Hash functions    : {stats['num_hash_functions']}")
print(f"Fill ratio        : {stats['fill_ratio']:.1%}")
print(f"Target FPR        : {stats['target_fpr']:.1%}")
print(f"Estimated FPR     : {stats['estimated_fpr']:.1%}")

# Verify: zero false negatives
all_found = all(bloom.might_contain(url) for url in malicious_urls)
print(f"\nZero false negatives: {all_found} (all {MALICIOUS_COUNT:,} malicious URLs found)")

# Measure actual false positive rate on unknown URLs
test_urls  = [random_url(14) for _ in range(10_000)]
false_positives = sum(1 for url in test_urls if bloom.might_contain(url))
actual_fpr = false_positives / len(test_urls)
print(f"False positive rate: {actual_fpr:.1%} (target: {FPR_TARGET:.1%})")
print(f"False positives    : {false_positives} out of {len(test_urls):,} clean URLs")
```

---

## 5. Image Processing — Pixel Bit Operations

### The Production Problem

Image processing libraries (PIL/Pillow, OpenCV, libpng) operate on pixels at
the bit level. An RGB pixel is packed as a 24-bit integer. Masking operations
extract individual channels. Alpha compositing uses bitwise blending. GPU
shaders use bitwise operations for texture sampling. Understanding pixel packing
and channel extraction is foundational to writing image filters, codecs, and
rendering pipelines.

```python
# -----------------------------------------------------------------------
# Pixel-level bit manipulation — foundation of image processing
# -----------------------------------------------------------------------

def pack_rgb(r: int, g: int, b: int) -> int:
    """
    Pack three 8-bit channel values into one 24-bit integer.
    Layout: 0xRRGGBB
    This is how pixels are stored in BMP files, CSS hex colors,
    and many texture formats.
    """
    r &= 0xFF   # clamp to 8 bits
    g &= 0xFF
    b &= 0xFF
    return (r << 16) | (g << 8) | b


def unpack_rgb(packed: int) -> tuple[int, int, int]:
    """Extract R, G, B channels from packed pixel using shifts and AND masks."""
    r = (packed >> 16) & 0xFF
    g = (packed >>  8) & 0xFF
    b = packed          & 0xFF
    return r, g, b


def pack_rgba(r: int, g: int, b: int, a: int) -> int:
    """Pack RGBA into 32-bit integer. Layout: 0xRRGGBBAA"""
    return (pack_rgb(r, g, b) << 8) | (a & 0xFF)


def unpack_rgba(packed: int) -> tuple[int, int, int, int]:
    r = (packed >> 24) & 0xFF
    g = (packed >> 16) & 0xFF
    b = (packed >>  8) & 0xFF
    a = packed          & 0xFF
    return r, g, b, a


def extract_channel(pixel: int, channel: str) -> int:
    """Extract a single color channel from a packed 24-bit RGB pixel."""
    shifts = {"r": 16, "g": 8, "b": 0}
    return (pixel >> shifts[channel]) & 0xFF


def apply_mask(image: list[int], mask: int) -> list[int]:
    """
    Apply a bitmask to every pixel in the image (flattened to 1D list).
    Used for: isolating color channels, bit-depth reduction, posterization.
    In OpenCV, cv2.bitwise_and(img, img, mask=mask) does exactly this.
    """
    return [pixel & mask for pixel in image]


def grayscale_pixel(r: int, g: int, b: int) -> int:
    """
    Convert RGB to grayscale using ITU-R BT.601 luma coefficients.
    The bit-shift approximation (used in embedded systems / fixed-point):
    Y ≈ (77*R + 150*G + 29*B) >> 8  (avoids floating point entirely)
    """
    return (77 * r + 150 * g + 29 * b) >> 8


def to_css_hex(r: int, g: int, b: int) -> str:
    """Convert to CSS hex color string. Same as pack_rgb but formatted."""
    return f"#{pack_rgb(r, g, b):06X}"


def invert_pixel(pixel: int) -> int:
    """Invert all channels: NOT operation masked to 24 bits."""
    return (~pixel) & 0xFFFFFF


def blend_pixels(pixel_a: int, pixel_b: int, alpha: float) -> int:
    """
    Alpha blend two pixels: result = alpha*A + (1-alpha)*B
    Demonstrates per-channel bit operations used in compositing engines.
    """
    ra, ga, ba = unpack_rgb(pixel_a)
    rb, gb, bb = unpack_rgb(pixel_b)
    alpha_int = int(alpha * 255) & 0xFF

    # Fixed-point alpha blend using bit shifts
    r = ((alpha_int * ra + (255 - alpha_int) * rb) >> 8) & 0xFF
    g = ((alpha_int * ga + (255 - alpha_int) * gb) >> 8) & 0xFF
    b = ((alpha_int * ba + (255 - alpha_int) * bb) >> 8) & 0xFF
    return pack_rgb(r, g, b)


# -----------------------------------------------------------------------
# Demo: pixel manipulation operations
# -----------------------------------------------------------------------

print("Pixel packing and channel extraction:")
test_pixels = [
    (255, 0,   0,   "Pure red"),
    (0,   255, 0,   "Pure green"),
    (0,   0,   255, "Pure blue"),
    (255, 165, 0,   "Orange"),
    (128, 0,   128, "Purple"),
    (30,  144, 255, "DodgerBlue"),
]

print(f"{'Color':<15} {'Packed':>10}  {'CSS Hex':>8}  R    G    B    Luma")
print("-" * 65)
for r, g, b, name in test_pixels:
    packed = pack_rgb(r, g, b)
    css    = to_css_hex(r, g, b)
    luma   = grayscale_pixel(r, g, b)
    r2, g2, b2 = unpack_rgb(packed)
    print(f"{name:<15} {packed:>10}  {css:>8}  {r2:3d}  {g2:3d}  {b2:3d}  {luma:3d}")

print("\nChannel isolation using bitmasks:")
orange = pack_rgb(255, 165, 0)
r_only_mask = 0xFF0000   # keep only red channel, zero others
g_only_mask = 0x00FF00
b_only_mask = 0x0000FF
print(f"  Orange (255, 165, 0) = 0x{orange:06X}")
print(f"  Red channel only     = 0x{orange & r_only_mask:06X}  -> R={extract_channel(orange, 'r')}")
print(f"  Green channel only   = 0x{orange & g_only_mask:06X}  -> G={extract_channel(orange, 'g')}")
print(f"  Blue channel only    = 0x{orange & b_only_mask:06X}  -> B={extract_channel(orange, 'b')}")

print("\nPixel operations:")
red   = pack_rgb(255, 0, 0)
blue  = pack_rgb(0, 0, 255)
r, g, b = unpack_rgb(blend_pixels(red, blue, alpha=0.5))
print(f"  Blend(red, blue, 50%) = rgb({r}, {g}, {b})  {to_css_hex(r, g, b)}")
r2, g2, b2 = unpack_rgb(invert_pixel(red))
print(f"  Invert(red)           = rgb({r2}, {g2}, {b2})  {to_css_hex(r2, g2, b2)}  (should be cyan)")
```

---

## 6. Cryptography Basics — XOR Cipher and Key Scheduling

### The Production Problem

XOR is the foundation of all stream ciphers (ChaCha20, RC4, Salsa20), block
cipher modes (CTR mode, OFB mode), and key derivation. AES in CTR mode is
essentially a sophisticated XOR cipher: encrypt a counter block to produce a
keystream, then XOR with the plaintext. Understanding why XOR is the right
operation — it is its own inverse, it preserves statistical uniformity, and it
is a single CPU instruction — is essential for understanding modern cryptography.

```python
import os
import hashlib
from typing import Union

# -----------------------------------------------------------------------
# XOR cipher — demonstrates why XOR is the cryptographic primitive
# -----------------------------------------------------------------------

def xor_encrypt(data: bytes, key: bytes) -> bytes:
    """
    Encrypt data using XOR with a repeating key (Vigenere XOR cipher).
    When key is as long as data and truly random, this is the One-Time Pad —
    the only provably unbreakable cipher.

    XOR properties that make it ideal for cryptography:
      1. a XOR b XOR b = a  (self-inverse — decryption == encryption)
      2. a XOR 0 = a        (identity element)
      3. a XOR a = 0        (self-cancellation)
      4. XOR of uniform random bits with any data = uniform random bits
    """
    key_len = len(key)
    return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))


def xor_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """
    Decryption is IDENTICAL to encryption — this is the self-inverse property.
    (ciphertext XOR key) XOR key = ciphertext XOR (key XOR key) = ciphertext XOR 0 = ciphertext
    """
    return xor_encrypt(ciphertext, key)  # same operation — XOR is its own inverse


def derive_keystream(password: str, length: int, salt: bytes = None) -> bytes:
    """
    Derive a cryptographic keystream from a password using PBKDF2.
    This is how real stream ciphers expand a short key into a full keystream.
    Real ciphers: ChaCha20 uses this concept but with a 256-bit key and nonce.
    """
    if salt is None:
        salt = b"demo_salt_not_for_production"
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations=100_000)
    # Extend key to required length using SHA-256 in counter mode
    keystream = b""
    counter = 0
    while len(keystream) < length:
        block = hashlib.sha256(key + counter.to_bytes(4, "big")).digest()
        keystream += block
        counter += 1
    return keystream[:length]


def xor_encrypt_with_key_derivation(plaintext: str, password: str) -> tuple[bytes, bytes]:
    """
    Full encrypt pipeline: derive keystream from password, XOR with plaintext.
    Returns (ciphertext, salt) — salt must be stored alongside ciphertext.
    """
    data  = plaintext.encode("utf-8")
    salt  = os.urandom(16)
    key   = derive_keystream(password, len(data), salt)
    ciphertext = xor_encrypt(data, key)
    return ciphertext, salt


def xor_decrypt_with_key_derivation(ciphertext: bytes, password: str, salt: bytes) -> str:
    """Full decrypt pipeline: re-derive keystream from password, XOR to recover plaintext."""
    key = derive_keystream(password, len(ciphertext), salt)
    return xor_decrypt(ciphertext, key).decode("utf-8")


def demonstrate_xor_properties() -> None:
    """Show the mathematical properties of XOR that make it useful in crypto."""
    print("XOR fundamental properties:")

    # Property 1: Self-inverse
    a, b = 0b10110100, 0b11001010
    print(f"  Self-inverse: ({a:08b} XOR {b:08b}) XOR {b:08b} = "
          f"{((a ^ b) ^ b):08b}  (got original a: {(a ^ b) ^ b == a})")

    # Property 2: XOR with 0 is identity
    print(f"  Identity:     {a:08b} XOR 0 = {a ^ 0:08b}  (unchanged: {a ^ 0 == a})")

    # Property 3: XOR with self is 0
    print(f"  Self-cancel:  {a:08b} XOR {a:08b} = {a ^ a:08b}  (zero: {a ^ a == 0})")

    # Property 4: Uniformity — XOR with random key produces uniform output
    import random
    random.seed(42)
    biased_data   = bytes([0b11111111] * 1000)  # all ones — maximum bias
    random_key    = bytes([random.randint(0, 255) for _ in range(1000)])
    encrypted     = xor_encrypt(biased_data, random_key)
    ones_count    = sum(bin(b).count("1") for b in encrypted)
    total_bits    = len(encrypted) * 8
    print(f"\n  Uniformity demonstration:")
    print(f"  Original data: {sum(bin(b).count('1') for b in biased_data)} ones out of {total_bits} bits (100% biased)")
    print(f"  After XOR enc: {ones_count} ones out of {total_bits} bits ({100*ones_count/total_bits:.1f}% — ~50%, uniform)")


# -----------------------------------------------------------------------
# Demo: XOR encryption round-trip
# -----------------------------------------------------------------------

demonstrate_xor_properties()

print("\n\nXOR cipher demo:")
message  = "Attack the north gate at dawn"
password = "supersecretpassword"

print(f"  Plaintext : {message!r}")

ciphertext, salt = xor_encrypt_with_key_derivation(message, password)
print(f"  Ciphertext: {ciphertext.hex()}")
print(f"  Salt      : {salt.hex()}")

recovered = xor_decrypt_with_key_derivation(ciphertext, password, salt)
print(f"  Decrypted : {recovered!r}")
print(f"  Round-trip: {message == recovered}")

# Show that wrong password produces garbage
wrong_key = derive_keystream("wrongpassword", len(ciphertext), salt)
wrong_dec = xor_decrypt(ciphertext, wrong_key)
try:
    wrong_text = wrong_dec.decode("utf-8", errors="replace")
except Exception:
    wrong_text = repr(wrong_dec)
print(f"\nWith wrong password: {wrong_text!r}  (garbled — decryption fails)")

# Simple byte-level XOR for illustration (without key derivation)
print("\nSimple XOR illustration:")
text     = b"Hello, World!"
key      = b"SECRET"
enc      = xor_encrypt(text, key)
dec      = xor_decrypt(enc, key)
print(f"  Original  : {text}")
print(f"  Key       : {key}")
print(f"  Encrypted : {enc.hex()}")
print(f"  Decrypted : {dec}")
print(f"  Matches   : {text == dec}")
```

---

## Summary Table

| Use Case | Core Operation | Bit Trick | Why Bits? |
|---|---|---|---|
| File permissions | AND (test), OR (grant), AND NOT (revoke) | 9-bit field per file | Single instruction permission check |
| Feature flags | AND (test), OR (enable), XOR (toggle) | 32 flags per integer | 1 int vs 32 columns in DB |
| Network masks | AND with mask | Prefix-to-mask shift | IP routing in kernel hot path |
| Bloom filter | OR (add), AND (test) | Double hashing to bit positions | 10x space savings vs hash set |
| Image pixels | Shift, AND, OR | Channel pack/unpack | Parallel 8-bit channel operations |
| XOR cipher | XOR | Self-inverse property | One instruction, no inverse to compute |

Every case exploits the same fundamental truth: **a single integer holds N
independent boolean values, and bitwise operations process all N simultaneously
in one CPU instruction**. This is why low-level systems think in bits.
