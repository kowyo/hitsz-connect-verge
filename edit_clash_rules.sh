#!/bin/zsh

YAML_FILE="$APPDATA\io.github.clash-verge-rev.clash-verge-rev\profiles\Rn6deUng0jJn.yaml"

NEW_PROXIES='- { name: "HITSZ Connect Verge", type: socks5, server: 127.0.0.1, port: 1080, udp: true }'
NEW_PROXY_GROUPS='    - { name: 校园网, type: select, proxies: ["DIRECT", "HITSZ Connect Verge"] }'
NEW_RULES='    - "DOMAIN,vpn.hitsz.edu.cn,DIRECT"\n    - "DOMAIN-SUFFIX,hitsz.edu.cn,校园网"\n    - "IP-CIDR,10.0.0.0/8,校园网,no-resolve"'

if ! grep -q "$NEW_PROXIES" "$YAML_FILE"; then
    if grep -q "^[[:space:]]*proxies:$" "$YAML_FILE"; then
        sed -i "/^[[:space:]]*proxies:$/a\\
    $NEW_PROXIES" "$YAML_FILE"
    else
        echo -e "proxies:\n$NEW_PROXIES" >> "$YAML_FILE"
    fi
fi

if grep -q "proxy-groups:" "$YAML_FILE"; then
    sed -i "/proxy-groups:/a\\
$NEW_PROXY_GROUPS" "$YAML_FILE"
else
    echo -e "proxy-groups:\n$NEW_PROXY_GROUPS" >> "$YAML_FILE"
fi

if grep -q "rules:" "$YAML_FILE"; then
    sed -i "/rules:/a\\
$NEW_RULES" "$YAML_FILE"
else
    echo -e "rules:\n$NEW_RULES" >> "$YAML_FILE"
fi

echo "Rules have been appended to $YAML_FILE."
