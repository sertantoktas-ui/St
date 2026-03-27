import 'dart:async';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:timezone/timezone.dart' as tz;
import '../data/countries.dart';

class ComparisonCard extends StatefulWidget {
  final Country country;
  final VoidCallback onRemove;

  const ComparisonCard({
    super.key,
    required this.country,
    required this.onRemove,
  });

  @override
  State<ComparisonCard> createState() => _ComparisonCardState();
}

class _ComparisonCardState extends State<ComparisonCard> {
  late Timer _timer;
  late DateTime _now;

  @override
  void initState() {
    super.initState();
    _now = _getTime();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      setState(() => _now = _getTime());
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  DateTime _getTime() {
    try {
      final loc = tz.getLocation(widget.country.timezone);
      return tz.TZDateTime.now(loc);
    } catch (_) {
      return DateTime.now();
    }
  }

  @override
  Widget build(BuildContext context) {
    final saat = DateFormat('HH:mm:ss').format(_now);
    final tarih = DateFormat('dd/MM/yyyy').format(_now);
    final gun = DateFormat('EEE', 'tr_TR').format(_now);

    return Container(
      width: 150,
      decoration: BoxDecoration(
        color: const Color(0xFF1e1e3a),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF3a3a6a), width: 1),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(widget.country.flag, style: const TextStyle(fontSize: 20)),
              GestureDetector(
                onTap: widget.onRemove,
                child: const Icon(Icons.close, color: Color(0xFF606080), size: 16),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            widget.country.name,
            style: const TextStyle(
              color: Color(0xFFa0a0c0),
              fontSize: 11,
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 10),
          Text(
            saat,
            style: const TextStyle(
              color: Color(0xFF00d4ff),
              fontSize: 20,
              fontWeight: FontWeight.bold,
              fontFamily: 'monospace',
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '$gun  $tarih',
            style: const TextStyle(
              color: Color(0xFF8080b0),
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }
}
